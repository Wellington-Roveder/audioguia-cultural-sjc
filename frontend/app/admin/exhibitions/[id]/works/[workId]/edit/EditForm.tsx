"use client"

import { FormEvent, useState } from "react"
import { useRouter } from "next/navigation"

type Work = {
  id: string
  exhibition_id: string
  title: string
  artist: string | null
  description: string
  audio_url: string | null
  audio_description_url: string | null
  libras_video_url: string | null
  public_slug: string
  is_active: boolean
}

type EditFormProps = {
  work: Work
  exhibitionId: string
}

export default function EditForm({
  work,
  exhibitionId,
}: EditFormProps) {
  const router = useRouter()

  const [title, setTitle] = useState(work.title)
  const [artist, setArtist] = useState(work.artist ?? "")
  const [description, setDescription] = useState(work.description)

  // Vídeo em Libras
  const [librasFile, setLibrasFile] = useState<File | null>(null)
  const [hasLibrasVideo, setHasLibrasVideo] = useState(
    Boolean(work.libras_video_url)
  )
  const [librasError, setLibrasError] = useState("")
  const [librasSuccess, setLibrasSuccess] = useState("")
  const [uploadingLibras, setUploadingLibras] = useState(false)

  const [isActive, setIsActive] = useState(work.is_active)

  // Áudio principal
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [hasAudio, setHasAudio] = useState(Boolean(work.audio_url))
  const [audioError, setAudioError] = useState("")
  const [audioSuccess, setAudioSuccess] = useState("")
  const [uploadingAudio, setUploadingAudio] = useState(false)

  // Audiodescrição
  const [audioDescriptionFile, setAudioDescriptionFile] =
    useState<File | null>(null)

  const [hasAudioDescription, setHasAudioDescription] =
    useState(Boolean(work.audio_description_url))

  const [audioDescriptionError, setAudioDescriptionError] =
    useState("")

  const [audioDescriptionSuccess, setAudioDescriptionSuccess] =
    useState("")

  const [
    uploadingAudioDescription,
    setUploadingAudioDescription,
  ] = useState(false)

  // Edição dos dados da obra
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    setError("")
    setSubmitting(true)

    try {
      const response = await fetch(
        `/api/admin/works/${work.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title,
            artist: artist || null,
            description,
            is_active: isActive,
          }),
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (!response.ok) {
        setError("Não foi possível atualizar a obra.")
        return
      }

      router.push(
        `/admin/exhibitions/${exhibitionId}/works`
      )
      router.refresh()
    } catch {
      setError("Não foi possível atualizar a obra.")
    } finally {
      setSubmitting(false)
    }
  }

  async function handleAudioUpload() {
    setAudioError("")
    setAudioSuccess("")

    if (!audioFile) {
      setAudioError("Selecione um arquivo MP3.")
      return
    }

    setUploadingAudio(true)

    try {
      const formData = new FormData()
      formData.append("file", audioFile)

      const response = await fetch(
        `/api/admin/works/${work.id}/media/audio`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (response.status === 413) {
        setAudioError(
          "O arquivo de áudio excede o limite de 10 MB."
        )
        return
      }

      if (response.status === 415) {
        setAudioError(
          "O arquivo selecionado não é um MP3 válido."
        )
        return
      }

      if (!response.ok) {
        setAudioError(
          "Não foi possível enviar o áudio."
        )
        return
      }

      setHasAudio(true)
      setAudioFile(null)
      setAudioSuccess("Áudio enviado com sucesso.")
      router.refresh()
    } catch {
      setAudioError(
        "Não foi possível enviar o áudio."
      )
    } finally {
      setUploadingAudio(false)
    }
  }

  async function handleAudioDescriptionUpload() {
    setAudioDescriptionError("")
    setAudioDescriptionSuccess("")

    if (!audioDescriptionFile) {
      setAudioDescriptionError(
        "Selecione um arquivo MP3."
      )
      return
    }

    setUploadingAudioDescription(true)

    try {
      const formData = new FormData()
      formData.append("file", audioDescriptionFile)

      const response = await fetch(
        `/api/admin/works/${work.id}/media/audio-description`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (response.status === 413) {
        setAudioDescriptionError(
          "O arquivo de audiodescrição excede o limite de 10 MB."
        )
        return
      }

      if (response.status === 415) {
        setAudioDescriptionError(
          "O arquivo selecionado não é um MP3 válido."
        )
        return
      }

      if (!response.ok) {
        setAudioDescriptionError(
          "Não foi possível enviar a audiodescrição."
        )
        return
      }

      setHasAudioDescription(true)
      setAudioDescriptionFile(null)

      setAudioDescriptionSuccess(
        "Audiodescrição enviada com sucesso."
      )

      router.refresh()
    } catch {
      setAudioDescriptionError(
        "Não foi possível enviar a audiodescrição."
      )
    } finally {
      setUploadingAudioDescription(false)
    }
  }

  async function handleLibrasUpload() {
    setLibrasError("")
    setLibrasSuccess("")

    if (!librasFile) {
      setLibrasError("Selecione um arquivo MP4.")
      return
    }

    setUploadingLibras(true)

    try {
      const formData = new FormData()
      formData.append("file", librasFile)

      const response = await fetch(
        `/api/admin/works/${work.id}/media/libras`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (response.status === 413) {
        setLibrasError("O vídeo excede o limite de 50 MB.")
        return
      }

      if (response.status === 415) {
        setLibrasError(
          "O arquivo selecionado não é um MP4 válido."
        )
        return
      }

      if (!response.ok) {
        setLibrasError(
          "Não foi possível enviar o vídeo em Libras."
        )
        return
      }

      setHasLibrasVideo(true)
      setLibrasFile(null)
      setLibrasSuccess(
        "Vídeo em Libras enviado com sucesso."
      )
      router.refresh()
    } catch {
      setLibrasError(
        "Não foi possível enviar o vídeo em Libras."
      )
    } finally {
      setUploadingLibras(false)
    }
  }
  return (
  <form
    className="admin-form-card admin-form"
    onSubmit={handleSubmit}
  >
    <div className="admin-field">
      <label htmlFor="title">Título</label>

      <input
        id="title"
        type="text"
        maxLength={150}
        value={title}
        onChange={(event) =>
          setTitle(event.target.value)
        }
        required
      />
    </div>

    <div className="admin-field">
      <label htmlFor="artist">Artista</label>

      <input
        id="artist"
        type="text"
        maxLength={150}
        value={artist}
        onChange={(event) =>
          setArtist(event.target.value)
        }
      />
    </div>

    <div className="admin-field">
      <label htmlFor="description">
        Descrição
      </label>

      <textarea
        id="description"
        rows={7}
        value={description}
        onChange={(event) =>
          setDescription(event.target.value)
        }
        required
      />
    </div>

    <div className="admin-media-section">
      <div className="admin-media-heading">
        <div>
          <h2>Recursos de acessibilidade</h2>
          <p>
            Gerencie os arquivos disponibilizados
            na página pública da obra.
          </p>
        </div>
      </div>

      <fieldset className="admin-media-card">
        <legend>Áudio da obra</legend>

        <p className="admin-media-status">
          {hasAudio
            ? "✓ Áudio cadastrado"
            : "Nenhum áudio cadastrado"}
        </p>

        <div className="admin-field">
          <label htmlFor="audio-file">
            Arquivo MP3
          </label>

          <input
            id="audio-file"
            type="file"
            accept="audio/mpeg,.mp3"
            onChange={(event) => {
              setAudioFile(
                event.target.files?.[0] ?? null
              )
              setAudioError("")
              setAudioSuccess("")
            }}
          />
        </div>

        {audioError && (
          <p
            className="admin-form-error"
            role="alert"
          >
            {audioError}
          </p>
        )}

        {audioSuccess && (
          <p
            className="admin-form-success"
            role="status"
          >
            {audioSuccess}
          </p>
        )}

        <button
          className="admin-secondary-button"
          type="button"
          onClick={handleAudioUpload}
          disabled={uploadingAudio || !audioFile}
        >
          {uploadingAudio
            ? "Enviando áudio..."
            : hasAudio
              ? "Substituir áudio"
              : "Enviar áudio"}
        </button>
      </fieldset>

      <fieldset className="admin-media-card">
        <legend>Audiodescrição</legend>

        <p className="admin-media-status">
          {hasAudioDescription
            ? "✓ Audiodescrição cadastrada"
            : "Nenhuma audiodescrição cadastrada"}
        </p>

        <div className="admin-field">
          <label htmlFor="audio-description-file">
            Arquivo MP3
          </label>

          <input
            id="audio-description-file"
            type="file"
            accept="audio/mpeg,.mp3"
            onChange={(event) => {
              setAudioDescriptionFile(
                event.target.files?.[0] ?? null
              )
              setAudioDescriptionError("")
              setAudioDescriptionSuccess("")
            }}
          />
        </div>

        {audioDescriptionError && (
          <p
            className="admin-form-error"
            role="alert"
          >
            {audioDescriptionError}
          </p>
        )}

        {audioDescriptionSuccess && (
          <p
            className="admin-form-success"
            role="status"
          >
            {audioDescriptionSuccess}
          </p>
        )}

        <button
          className="admin-secondary-button"
          type="button"
          onClick={handleAudioDescriptionUpload}
          disabled={
            uploadingAudioDescription ||
            !audioDescriptionFile
          }
        >
          {uploadingAudioDescription
            ? "Enviando audiodescrição..."
            : hasAudioDescription
              ? "Substituir audiodescrição"
              : "Enviar audiodescrição"}
        </button>
      </fieldset>

      <fieldset className="admin-media-card">
        <legend>Vídeo em Libras</legend>

        <p className="admin-media-status">
          {hasLibrasVideo
            ? "✓ Vídeo em Libras cadastrado"
            : "Nenhum vídeo em Libras cadastrado"}
        </p>

        <div className="admin-field">
          <label htmlFor="libras-file">
            Arquivo MP4
          </label>

          <input
            id="libras-file"
            type="file"
            accept="video/mp4,.mp4"
            onChange={(event) => {
              setLibrasFile(
                event.target.files?.[0] ?? null
              )
              setLibrasError("")
              setLibrasSuccess("")
            }}
          />
        </div>

        {librasError && (
          <p
            className="admin-form-error"
            role="alert"
          >
            {librasError}
          </p>
        )}

        {librasSuccess && (
          <p
            className="admin-form-success"
            role="status"
          >
            {librasSuccess}
          </p>
        )}

        <button
          className="admin-secondary-button"
          type="button"
          onClick={handleLibrasUpload}
          disabled={uploadingLibras || !librasFile}
        >
          {uploadingLibras
            ? "Enviando vídeo..."
            : hasLibrasVideo
              ? "Substituir vídeo em Libras"
              : "Enviar vídeo em Libras"}
        </button>
      </fieldset>
    </div>

    <label className="admin-checkbox">
      <input
        type="checkbox"
        checked={isActive}
        onChange={(event) =>
          setIsActive(event.target.checked)
        }
      />

      <span>Obra ativa</span>
    </label>

    {error && (
      <p
        className="admin-form-error"
        role="alert"
      >
        {error}
      </p>
    )}

    <div className="admin-form-actions">
      <button
        className="admin-submit-button"
        type="submit"
        disabled={submitting}
      >
        {submitting
          ? "Salvando..."
          : "Salvar alterações"}
      </button>

      <button
        className="admin-cancel-link"
        type="button"
        onClick={() =>
          router.push(
            `/admin/exhibitions/${exhibitionId}/works`
          )
        }
      >
        Cancelar
      </button>
    </div>
  </form>
)
 
}