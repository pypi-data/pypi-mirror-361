from mstt.plugin import hookimpl
from .models import FunASRModel


@hookimpl
def register_models(registry):
    """Registers FunASR models with the central registry."""

    registry.register("funasr/iic/SenseVoiceSmall", FunASRModel)
    registry.register("sensevoice_small", FunASRModel)

    registry.register("funasr/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch", FunASRModel)
    registry.register("paraformer-zh", FunASRModel)

    registry.register("funasr/iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020", FunASRModel)
    registry.register("paraformer-en", FunASRModel)

    registry.register("funasr/iic/speech_conformer_asr-en-16k-vocab4199-pytorch", FunASRModel)
    registry.register("conformer-en", FunASRModel)

    registry.register("funasr/iic/Whisper-large-v3", FunASRModel)
    registry.register("whisper-large-v3", FunASRModel)

    registry.register("funasr/iic/Whisper-large-v3-turbo", FunASRModel)
    registry.register("whisper-large-v3-turbo", FunASRModel)
