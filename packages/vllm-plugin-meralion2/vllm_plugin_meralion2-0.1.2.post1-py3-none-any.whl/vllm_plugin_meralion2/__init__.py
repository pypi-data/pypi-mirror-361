from typing import Optional

from vllm.entrypoints.chat_utils import BaseMultiModalItemTracker

from .transformers_utils.no_repeat_logits_processor import NoRepeatNGramLogitsProcessor


_original_placeholder_str = BaseMultiModalItemTracker._placeholder_str


def custom_placeholder_str(self, modality,
                        current_count: int) -> Optional[str]:
    hf_config = self._model_config.hf_config
    model_type = hf_config.model_type

    if modality == "audio" and model_type == "meralion2":
        return "<SpeechHere>"

    return _original_placeholder_str(self, modality=modality, current_count=current_count)


def register():
    import vllm
    from vllm import ModelRegistry

    v064_compatible_versions = ['0.6.5', '0.6.6', '0.6.6.post1', '0.7.0', '0.7.1', '0.7.2', '0.7.3']
    v085_compatible_versions = ['0.8.5', '0.8.5.post1']
    sorted_compatible_versions = sorted(v064_compatible_versions + v085_compatible_versions)

    if vllm.__version__ in v064_compatible_versions:
        from .vllm064_post1 import MERaLiON2ForConditionalGeneration
    elif vllm.__version__ in v085_compatible_versions:
        from .vllm085 import MERaLiON2ForConditionalGeneration
    else:
        raise Exception((
            f"MERaLiON2 doesn't support vLLM version {vllm.__version__}."
            f" Supported vLLM versions: {', '.join((sorted_compatible_versions))}"
            ))

    if "MERaLiON2ForConditionalGeneration" not in ModelRegistry.get_supported_archs():
        ModelRegistry.register_model(
            "MERaLiON2ForConditionalGeneration",
            MERaLiON2ForConditionalGeneration
            )
        
    vllm.entrypoints.chat_utils.BaseMultiModalItemTracker._placeholder_str = custom_placeholder_str