"""Inference-only MERaLiON AudioLLM model compatible with HuggingFace weights."""
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Optional, Set, Tuple, TypedDict, Union, List

import math
import torch
import torch.nn as nn
from transformers import BatchFeature
from transformers.models.whisper.modeling_whisper import WhisperEncoder
from transformers.models.whisper.feature_extraction_whisper import WhisperFeatureExtractor

from vllm.config import VllmConfig
from vllm.model_executor.sampling_metadata import SamplingMetadata
from vllm.multimodal import MULTIMODAL_REGISTRY, MultiModalKwargs
from vllm.multimodal.inputs import (MultiModalDataDict, MultiModalFieldConfig,
                                    MultiModalKwargs)
from vllm.multimodal.parse import (AudioProcessorItems, MultiModalDataItems,
                                   MultiModalDataParser)
from vllm.multimodal.processing import (BaseMultiModalProcessor,
                                        BaseProcessingInfo, PromptReplacement,
                                        PromptUpdate, PromptUpdateDetails)
from vllm.multimodal.profiling import BaseDummyInputsBuilder
from vllm.sequence import IntermediateTensors
from vllm.model_executor.models.interfaces import MultiModalEmbeddings, SupportsMultiModal, SupportsPP
from vllm.model_executor.models.utils import (AutoWeightsLoader, init_vllm_registered_model,
                    maybe_prefix, merge_multimodal_embeddings)

from .transformers_utils.processing_meralion2 import MERaLiON2Processor
from .transformers_utils.configuration_meralion2 import MERaLiON2Config
from .transformers_utils.modules import (autoset_attn_implementation_for_whisper,
    MERaLiON2Inputs, MERaLiON2SpeechAudioAdaper)


class MERaLiON2ProcessingInfo(BaseProcessingInfo):

    def get_hf_config(self):
        return self.ctx.get_hf_config(MERaLiON2Config)

    def get_hf_processor(
        self,
        *,
        # Ignored in initialization
        sampling_rate: Optional[int] = None,
        **kwargs: object,
    ) -> MERaLiON2Processor:
        return self.ctx.get_hf_processor(MERaLiON2Processor, **kwargs)

    def get_feature_extractor(
        self,
        *,
        # Ignored in initialization
        sampling_rate: Optional[int] = None,
    ) -> WhisperFeatureExtractor:
        hf_processor = self.get_hf_processor(sampling_rate=sampling_rate)
        feature_extractor = hf_processor.feature_extractor  # type: ignore
        assert isinstance(feature_extractor, WhisperFeatureExtractor)
        return feature_extractor

    def get_supported_mm_limits(self) -> Mapping[str, Optional[int]]:
        return {"audio": None}
    

class MERaLiON2DummyInputsBuilder(
        BaseDummyInputsBuilder[MERaLiON2ProcessingInfo]):

    def get_dummy_text(self, mm_counts: Mapping[str, int]) -> str:
        num_audios = mm_counts.get("audio", 0)

        hf_processor = self.info.get_hf_processor()
        audio_token = hf_processor.speech_token

        return audio_token * num_audios

    def get_dummy_mm_data(
        self,
        seq_len: int,
        mm_counts: Mapping[str, int],
    ) -> MultiModalDataDict:
        processor = self.info.get_hf_processor()
        feature_extractor = self.info.get_feature_extractor()

        # This is to specify the audio length
        num_chunk_limit = processor.number_chunk_limit
        sampling_rate = feature_extractor.sampling_rate
        audio_len = num_chunk_limit * feature_extractor.chunk_length * sampling_rate 
        num_audios = mm_counts.get("audio", 0)

        return {
            "audio":
            self._get_dummy_audios(length=audio_len, num_audios=num_audios)
        }
    

class MERaLiON2MultiModalProcessor(
        BaseMultiModalProcessor[MERaLiON2ProcessingInfo]):

    def _get_data_parser(self) -> MultiModalDataParser:
        feature_extractor = self.info.get_feature_extractor()
        return MultiModalDataParser(target_sr=feature_extractor.sampling_rate)

    def _call_hf_processor(
        self,
        prompt: str,
        mm_data: Mapping[str, object],
        mm_kwargs: Mapping[str, Any],
    ) -> BatchFeature:
        # Text-only input not supported in composite processor
        if not mm_data.get("audios", []):
            prompt_ids = self.info.get_tokenizer().encode(prompt)
            prompt_ids = self._apply_hf_processor_tokens_only(prompt_ids)
            return BatchFeature(dict(input_ids=[prompt_ids]), tensor_type="pt")

        processor = self.info.get_hf_processor()
        feature_extractor = self.info.get_feature_extractor(**mm_kwargs)
        speech_token_id = getattr(processor, "speech_token_index", 255999)
        output_chunk_size = getattr(processor, "fixed_speech_embeds_length", 100)

        mm_kwargs = dict(
            **mm_kwargs,
            sampling_rate=feature_extractor.sampling_rate,
        )

        results = super()._call_hf_processor(
            prompt=prompt,
            mm_data=mm_data,
            mm_kwargs=mm_kwargs,
        )

        chunk_sizes = (results["input_ids"] == speech_token_id).sum(axis=1) // output_chunk_size
        splitted_input_features = torch.split(results["input_features"], chunk_sizes.tolist())
        splitted_feature_attention_mask = torch.split(results["feature_attention_mask"], chunk_sizes.tolist())

        results["input_features"] = splitted_input_features
        results["feature_attention_mask"] = splitted_feature_attention_mask
        return results
        
    def _get_mm_fields_config(
        self,
        hf_inputs: BatchFeature,
        hf_processor_mm_kwargs: Mapping[str, object],
    ) -> Mapping[str, MultiModalFieldConfig]:
        return dict(
            input_features=MultiModalFieldConfig.batched("audio"),
            feature_attention_mask=MultiModalFieldConfig.batched("audio"),
        )

    def _get_prompt_updates(
        self,
        mm_items: MultiModalDataItems,
        hf_processor_mm_kwargs: Mapping[str, object],
        out_mm_kwargs: MultiModalKwargs,
    ) -> Sequence[PromptUpdate]:
        processor = self.info.get_hf_processor(**hf_processor_mm_kwargs)

        speech_token = getattr(processor, "audio_token", "<SpeechHere>")
        speech_token_id = getattr(processor, "speech_token_index", 255999)
        output_chunk_size = getattr(processor, "fixed_speech_embeds_length", 100)
        feature_chunk_size = getattr(processor, "feature_chunk_size", 30 * 16000)

        def get_replacement_meralion2_audio(item_idx: int):
            audios = mm_items.get_items("audio", AudioProcessorItems)
            audio_length = audios.get_audio_length(item_idx)
            number_chunks = ((audio_length - 1) // feature_chunk_size) + 1
            speech_tokens = [speech_token_id] * number_chunks * output_chunk_size

            return PromptUpdateDetails.select_token_id(
                speech_tokens,
                embed_token_id=speech_token_id,
            )

        return [
            PromptReplacement(
                modality="audio",
                target=speech_token,
                replacement=get_replacement_meralion2_audio,
            )
        ]
    

@MULTIMODAL_REGISTRY.register_processor(
    MERaLiON2MultiModalProcessor,
    info=MERaLiON2ProcessingInfo,
    dummy_inputs=MERaLiON2DummyInputsBuilder)
class MERaLiON2ForConditionalGeneration(nn.Module, SupportsMultiModal,
                                         SupportsPP):

    def __init__(self, *, vllm_config: VllmConfig, prefix: str = ""):
        super().__init__()
        config = vllm_config.model_config.hf_config
        quant_config = vllm_config.quant_config
        multimodal_config = vllm_config.model_config.multimodal_config
        self.config = config
        self.multimodal_config = multimodal_config

        config.speech_config = \
            autoset_attn_implementation_for_whisper(config.speech_config)
        self.speech_encoder = WhisperEncoder(config.speech_config)
        self.ln_speech = nn.LayerNorm(config.speech_config.d_model)
        self.speech_audio_adapter = MERaLiON2SpeechAudioAdaper(
            config.speech_config.d_model, config.text_config.hidden_size)

        self.quant_config = quant_config

        self.text_decoder = init_vllm_registered_model(
            vllm_config=vllm_config,
            hf_config=config.text_config,
            prefix=maybe_prefix(prefix, "text_decoder"),
            architectures=["Gemma2ForCausalLM"],
        )

        self.make_empty_intermediate_tensors = (
            self.text_decoder.make_empty_intermediate_tensors)

    def _validate_and_reshape_mm_tensor(self,
                                        mm_input: Union[torch.Tensor,
                                                        List[torch.Tensor]],
                                        name: str) -> torch.Tensor:
        if not isinstance(mm_input, (torch.Tensor, list)):
            raise ValueError(f"Incorrect type of {name}. "
                             f"Got type: {type(mm_input)}")
        
        input_ids_lst = mm_input.size()
        with open("log.txt", "a") as f:
            f.write(",".join([str(e) for e in input_ids_lst]) + "\n")

        if isinstance(mm_input, torch.Tensor):
            result = torch.concat(list(mm_input))            
        else:
            result = torch.concat(mm_input)

        flattened_result = result.view(-1, result.size(-2), result.size(-1))
        return flattened_result

    def _parse_and_validate_audio_input(
            self, **kwargs: object) -> Optional[MERaLiON2Inputs]:
        input_features = kwargs.pop('input_features', None)
        feature_attention_mask = kwargs.pop('feature_attention_mask', None)

        if input_features is None:
            return None
        input_features = self._validate_and_reshape_mm_tensor(
            input_features, 'input_features')
        feature_attention_mask = self._validate_and_reshape_mm_tensor(
            feature_attention_mask, 'feature_attention_mask')
        if not isinstance(input_features, (torch.Tensor, list)):
            raise ValueError("Incorrect type of audio input features. "
                             f"Got type: {type(input_features)}")
        return MERaLiON2Inputs(input_features=input_features,
                                feature_attention_mask=feature_attention_mask)

    def _process_audio_input(self,
                             audio_input: MERaLiON2Inputs) -> torch.Tensor:
        
        input_features = audio_input["input_features"].to(self.speech_encoder.dtype)
        feature_attention_mask = audio_input["feature_attention_mask"]

        audio_outputs = self.speech_encoder(input_features,
                                         attention_mask=feature_attention_mask)
        audio_features = audio_outputs.last_hidden_state
        audio_features = self.ln_speech(audio_features)
        audio_features = self.speech_audio_adapter(audio_features)
        audio_features = audio_features.view(-1, audio_features.size(-1))
        
        return audio_features
    
    def get_language_model(self) -> torch.nn.Module:
        return self.text_decoder
    
    def get_multimodal_embeddings(
            self, **kwargs: object) -> Optional[MultiModalEmbeddings]:
        
        if "input_features" not in kwargs:
            return None
        
        input_features = kwargs["input_features"]
        audio_input = self._parse_and_validate_audio_input(**kwargs)        
        if isinstance(input_features, torch.Tensor):
            input_features = list(input_features)
        
        audio_lengths = [math.prod(audio.shape[:-2]) * 100 for audio in input_features]
        masked_audio_features = self._process_audio_input(audio_input)
        masked_audio_features = torch.split(masked_audio_features, audio_lengths)
        return masked_audio_features
    
    def get_input_embeddings(
        self,
        input_ids: torch.Tensor,
        multimodal_embeddings: Optional[MultiModalEmbeddings] = None,
    ) -> torch.Tensor:
        inputs_embeds = self.text_decoder.get_input_embeddings(input_ids)
        if multimodal_embeddings is not None:
            inputs_embeds = merge_multimodal_embeddings(
                input_ids, inputs_embeds, multimodal_embeddings,
                self.config.speech_token_index)
        return inputs_embeds

    def forward(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        intermediate_tensors: Optional[IntermediateTensors] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        **kwargs: object,
    ) -> Union[torch.Tensor, IntermediateTensors]:        
        if intermediate_tensors is not None:
            inputs_embeds = None

        # NOTE: In v1, inputs_embeds is always generated at model runner, this
        # condition is for v0 compatibility.
        elif inputs_embeds is None:
            multimodal_embeddings = self.get_multimodal_embeddings(**kwargs)
            inputs_embeds = self.get_input_embeddings(input_ids,
                                                      multimodal_embeddings)
            input_ids = None

        hidden_states = self.text_decoder.model(input_ids,
                                                  positions,
                                                  intermediate_tensors,
                                                  inputs_embeds=inputs_embeds)
        return hidden_states

    def compute_logits(
        self,
        hidden_states: torch.Tensor,
        sampling_metadata: SamplingMetadata,
    ) -> Optional[torch.Tensor]:
        return self.text_decoder.compute_logits(hidden_states,
                                                  sampling_metadata)
    
    def load_weights(self, weights: Iterable[Tuple[str,
                                                   torch.Tensor]]) -> Set[str]:
        loader = AutoWeightsLoader(self)
        return loader.load_weights(weights)
