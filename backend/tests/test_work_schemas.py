from uuid import uuid4

import pytest
from app.schemas.work import WorkCreate, WorkUpdate
from pydantic import ValidationError


def test_work_create_accepts_valid_data():
    exhibition_id = uuid4()

    work = WorkCreate(
        exhibition_id=exhibition_id,
        title="Memórias do Vale",
        artist="Artista Teste",
        description="Descrição da obra.",
    )

    assert work.exhibition_id == exhibition_id
    assert work.title == "Memórias do Vale"
    assert work.artist == "Artista Teste"
    assert work.description == "Descrição da obra."
    assert work.audio_url is None
    assert work.audio_description_url is None
    assert work.libras_video_url is None


def test_work_create_accepts_optional_media():
    work = WorkCreate(
        exhibition_id=uuid4(),
        title="Obra com Mídia",
        description="Descrição da obra.",
        audio_url="https://example.com/audio.mp3",
        audio_description_url="https://example.com/audiodescricao.mp3",
        libras_video_url="https://example.com/libras.mp4",
    )

    assert work.audio_url == "https://example.com/audio.mp3"
    assert work.audio_description_url == "https://example.com/audiodescricao.mp3"
    assert work.libras_video_url == "https://example.com/libras.mp4"


def test_work_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="",
            description="Descrição válida.",
        )


def test_work_create_rejects_title_longer_than_150_characters():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="a" * 151,
            description="Descrição válida.",
        )


def test_work_create_rejects_empty_description():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="Obra válida",
            description="",
        )


def test_work_create_rejects_artist_longer_than_150_characters():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="Obra válida",
            artist="a" * 151,
            description="Descrição válida.",
        )


def test_work_update_allows_partial_update():
    update = WorkUpdate(
        title="Novo título",
    )

    assert update.title == "Novo título"
    assert update.model_fields_set == {"title"}


def test_work_update_allows_clearing_optional_field():
    update = WorkUpdate(
        artist=None,
    )

    assert "artist" in update.model_fields_set
    assert update.artist is None


def test_work_create_rejects_blank_title():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="   ",
            description="Descrição válida.",
        )


def test_work_create_rejects_blank_description():
    with pytest.raises(ValidationError):
        WorkCreate(
            exhibition_id=uuid4(),
            title="Obra válida",
            description="   ",
        )
