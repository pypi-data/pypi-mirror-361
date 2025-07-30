from typing import List, Optional

from pydantic import BaseModel


class Segment(BaseModel):
    """
    Represents a single segment of transcribed audio with its start and end times.

    Attributes:
        start (float): The start time of the segment in seconds.
        end (float): The end time of the segment in seconds.
        text (str): The transcribed text for this segment.
        confidence (Optional[float]): The confidence score for the transcription of this segment, if available.
    """

    start: float
    end: float
    text: str
    confidence: Optional[float] = None


class TranscriptionResult(BaseModel):
    """
    Represents the complete structured result of an audio transcription.

    Attributes:
        text (str): The full concatenated transcribed text of the entire audio.
        segments (List[Segment]): A list of `Segment` objects, providing detailed timing and text for each part of the audio.
        language (Optional[str]): The detected language of the transcribed audio, if available.
        model_id (str): The identifier of the model used for transcription.
    """

    text: str
    segments: List[Segment]
    language: Optional[str] = None
    model_id: str
