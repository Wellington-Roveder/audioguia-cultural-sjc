from app.schemas.public_work import PublicWorkRead


def test_public_work_schema_accepts_public_fields():
    data = PublicWorkRead(
        title="Caminhos do Vale",
        artist="Artista Fictício",
        description="Descrição da obra.",
        audio_url=None,
        audio_description_url=None,
        libras_video_url=None,
    )

    assert data.title == "Caminhos do Vale"
    assert data.artist == "Artista Fictício"
