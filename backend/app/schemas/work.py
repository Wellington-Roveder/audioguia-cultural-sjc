from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


NonBlankText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]

NonBlankTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=150,
    ),
]


class WorkCreate(BaseModel):
    exhibition_id: UUID

    title: NonBlankTitle

    artist: str | None = Field(
        default=None,
        max_length=150,
    )

    description: NonBlankText

    audio_url: str | None = None
    audio_description_url: str | None = None
    libras_video_url: str | None = None


class WorkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exhibition_id: UUID
    title: str
    artist: str | None
    description: str

    audio_url: str | None
    audio_description_url: str | None
    libras_video_url: str | None

    public_slug: str
    is_active: bool


class WorkUpdate(BaseModel):
    title: NonBlankTitle | None = None

    artist: str | None = Field(
        default=None,
        max_length=150,
    )

    description: NonBlankText | None = None

    audio_url: str | None = None
    audio_description_url: str | None = None
    libras_video_url: str | None = None

    is_active: bool | None = None
