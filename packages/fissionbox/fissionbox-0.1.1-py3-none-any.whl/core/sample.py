
from pydantic import BaseModel, Field
import datetime
from typing import Optional
from enum import Enum

class SampleType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class Sample(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="The unique identifier for the sample.",
    )
    name: str = Field(
        ...,
        description="The name of the sample to be created.",
    )
    type: Optional[SampleType] = Field(
        default=None,
        description="The type of the sample (e.g., image, video, audio, text).",
    )
    media: Optional[dict] = Field(
        default=None,
        description="Additional media attributes associated with the sample.",
    )
