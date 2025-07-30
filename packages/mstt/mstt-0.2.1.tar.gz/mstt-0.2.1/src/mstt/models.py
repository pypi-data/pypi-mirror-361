# asr/models.py
import abc
from pathlib import Path
from typing import Dict, Type, Union

from .types import Segment, TranscriptionResult

try:
    import torch
    import transformers
except ImportError:
    torch = None
    transformers = None


class AsrModel(abc.ABC):
    """Abstract base class for all ASR models."""

    def __init__(self, model_id: str):
        """
        Initializes the ASR model with a given ID.

        Args:
            model_id (str): A unique identifier for the model.
        """
        self.model_id = model_id

    @abc.abstractmethod
    def transcribe(self, audio: Union[str, bytes]) -> TranscriptionResult:
        """
        Transcribes an audio file.

        Args:
            audio: Path to the audio file (str) or audio bytes.

        Returns:
            A TranscriptionResult object.
        """
        raise NotImplementedError


class ModelRegistry:
    """
    Manages the registration and retrieval of ASR model classes.

    This registry allows different ASR model implementations to be
    registered and looked up by a unique name or ID.
    """

    def __init__(self):
        """
        Initializes an empty model registry.
        """
        self.models: Dict[str, Type[AsrModel]] = {}

    def register(self, name: str, model_class: Type[AsrModel]):
        """
        Registers an ASR model class with a given name.

        Args:
            name (str): The unique name or ID for the model.
            model_class (Type[AsrModel]): The class of the ASR model to register.
        """
        self.models[name] = model_class

    def get_class(self, name: str) -> Type[AsrModel] | None:
        """
        Retrieves a registered ASR model class by its name.

        Args:
            name (str): The name or ID of the model class to retrieve.

        Returns:
            Type[AsrModel] | None: The ASR model class if found, otherwise None.
        """
        return self.models.get(name)


class TransformersModel(AsrModel):
    """
    A generic ASR model powered by the Hugging Face transformers library.
    It can load any ASR model from the Hub that is supported by the
    "automatic-speech-recognition" pipeline.
    """

    def __init__(self, model_id: str):
        if transformers is None:
            raise ImportError(
                "The 'transformers' library is not installed. "
                "Please install it with: pip install mstt[transformers]"
            )
        super().__init__(model_id)
        self._pipeline = None
        self._device = "cuda:0" if torch.cuda.is_available() else "cpu"

    def _load_pipeline(self):
        """
        Lazy-loads the Hugging Face ASR pipeline on first use.

        This method initializes the `transformers.pipeline` for automatic
        speech recognition, ensuring the model is loaded only when needed.
        It prints loading messages to the console.
        """
        if self._pipeline is None:
            print(f"Loading model '{self.model_id}' on device '{self._device}'...")
            self._pipeline = transformers.pipeline(
                "automatic-speech-recognition",
                model=self.model_id,
                device=self._device,
            )
            print("Model loaded.")

    def _read_audio(self, audio: Union[str, bytes, Path]) -> bytes:
        """
        Reads audio input into bytes format.

        Args:
            audio (Union[str, bytes, Path]): The audio input, which can be a file path
                                              (string or Path object) or raw bytes.

        Returns:
            bytes: The audio content as bytes.

        Raises:
            TypeError: If the audio input is not a string, Path object, or bytes.
        """
        if isinstance(audio, bytes):
            return audio
        if isinstance(audio, (str, Path)):
            with open(audio, "rb") as f:
                return f.read()
        raise TypeError("Audio must be a file path (str), Path object, or bytes.")

    def transcribe(self, audio: Union[str, bytes, Path]) -> TranscriptionResult:
        self._load_pipeline()
        audio_bytes = self._read_audio(audio)

        # Use long-form transcription arguments for robustness
        result = self._pipeline(
            audio_bytes,
            chunk_length_s=30,
            stride_length_s=5,
            return_timestamps="word",
        )

        segments = []
        # if "chunks" in result:
        #     for chunk in result.get("chunks", []):
        #         start, end = chunk["timestamp"]
        #         segments.append(
        #             Segment(start=start, end=end, text=chunk["text"].strip())
        #         )

        # Whisper models might not have language in pipeline output
        # Here we could add logic to detect it if needed
        language = result.get("language", None)

        return TranscriptionResult(
            text=result["text"],
            segments=segments,
            language=language,
            model_id=self.model_id,
        )
