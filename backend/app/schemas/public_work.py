from pydantic import BaseModel


class PublicWorkRead(BaseModel):
    title: str
    artist: str | None
    description: str
    audio_url: str | None
    audio_description_url: str | None
    libras_video_url: str | None
