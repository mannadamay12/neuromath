from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    SPANISH = "Spanish"
    MANDARIN = "Mandarin"
    TURKISH = "Turkish"
    TAMIL = "Tamil"

class VoiceModel(BaseModel):
    language: Language = Field(..., description="Language for video narration")
    voice_label: str = Field(..., description="Voice ID for the TTS service")

class VideoRequest(BaseModel):
    math_problem: str = Field(..., description="The math topic or problem to explain")
    audience_age: str = Field(..., description="Target audience age (e.g., '10', 'Undergraduate')")
    language: Language = Field(default=Language.ENGLISH, description="Language for video narration")
    voice_label: Optional[str] = Field(default="en-US-AriaNeural", description="Voice ID for the TTS service")

class VideoResponse(BaseModel):
    video_id: str = Field(..., description="Unique identifier for the video")
    video_url: str = Field(..., description="URL to access the generated video")
    status: str = Field(..., description="Status of the video generation process")
    message: Optional[str] = None