from typing import Union
from pathlib import Path

# 从核心库导入基类和类型
from mstt.models import AsrModel
from mstt.types import TranscriptionResult, Segment


try:
    import torch
    from funasr import AutoModel
    from funasr.utils.postprocess_utils import rich_transcription_postprocess
except ImportError:
    # 理论上，既然这是一个 funasr 插件，这些依赖应该存在。
    # 但作为防御性编程，这样做是安全的。
    AutoModel = None
    rich_transcription_postprocess = None


class FunASRModel(AsrModel):
    """
    An ASR model powered by FunASR's AutoModel.
    The model_id is expected to be in the format 'funasr/<ModelScope_ID>',
    e.g., 'funasr/iic/SenseVoiceSmall'.
    """

    MODEL_ID_MAPPING = {
        "funasr/iic/SenseVoiceSmall": "iic/SenseVoiceSmall",
        "sensevoice_small": "iic/SenseVoiceSmall",
        "funasr/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "paraformer-zh": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "funasr/iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020": "iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020",
        "paraformer-en": "iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020",
        "funasr/iic/speech_conformer_asr-en-16k-vocab4199-pytorch": "iic/speech_conformer_asr-en-16k-vocab4199-pytorch",
        "conformer-en": "iic/speech_conformer_asr-en-16k-vocab4199-pytorch",
        "funasr/iic/Whisper-large-v3": "iic/Whisper-large-v3",
        "whisper-large-v3": "iic/Whisper-large-v3",
        "funasr/iic/Whisper-large-v3-turbo": "iic/Whisper-large-v3-turbo",
        "whisper-large-v3-turbo": "iic/Whisper-large-v3-turbo",
    }
    PREFIX = "funasr/"

    def __init__(self, model_id: str):
        if AutoModel is None:
            raise ImportError("The 'funasr' library is not installed. " "Please install it to use FunASR models.")
        super().__init__(model_id)
        self._model = None
        self._device = "cuda:0" if torch.cuda.is_available() else "cpu"

        # Resolve the actual ModelScope ID
        if model_id in self.MODEL_ID_MAPPING:
            self.funasr_model_id = self.MODEL_ID_MAPPING[model_id]
        elif model_id.startswith(self.PREFIX):
            self.funasr_model_id = model_id[len(self.PREFIX) :]
        else:
            # This case should ideally not be reached if registry is set up correctly
            raise ValueError(f"Invalid FunASR model ID format: {model_id}")

    def _load_model(self):
        """Lazy-loads the FunASR model on first use."""
        if self._model is None:
            print(f"Loading FunASR model '{self.funasr_model_id}' on device '{self._device}'...")
            # 这些参数可以作为未来CLI的选项
            self._model = AutoModel(
                model=self.funasr_model_id,
                # vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},
                device=self._device,
            )
            print("Model loaded.")

    def transcribe(self, audio: Union[str, bytes, Path]) -> TranscriptionResult:
        self._load_model()

        # FunASR的generate方法似乎更喜欢文件路径
        # 如果是bytes，我们需要将其保存为临时文件，但这会增加复杂性。
        # 目前，我们假设输入是文件路径，这与CLI的使用方式一致。
        if isinstance(audio, bytes):
            # TODO: Handle bytes input, e.g., by writing to a temporary file.
            raise NotImplementedError("FunASR plugin currently only supports file path inputs.")

        # 这些参数也可以通过CLI选项进行配置
        res = self._model.generate(
            input=str(audio),  # 确保是字符串路径
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )

        # FunASR的输出是一个列表，我们处理第一个结果
        if not res:
            return TranscriptionResult(text="", segments=[], model_id=self.model_id)

        first_result = res[0]

        # 'text' 字段包含带有时间戳的富文本
        # 我们需要解析它，或者使用后处理函数得到纯文本
        full_text = rich_transcription_postprocess(first_result.get("text", ""))

        # FunASR 的 generate 结果中可能有 'sentence_info'
        segments = []
        if "sentence_info" in first_result:
            for sentence in first_result["sentence_info"]:
                segments.append(
                    Segment(
                        start=sentence["start"] / 1000.0,  # 毫秒转秒
                        end=sentence["end"] / 1000.0,
                        text=sentence["text"].strip(),
                    )
                )

        return TranscriptionResult(
            text=full_text,
            segments=segments,
            # FunASR 的结果中没有直接的语言字段，但可以从输入参数中获得
            language=None,  # Or reflect the input language parameter
            model_id=self.model_id,
        )
