"use client"

import { FormEvent, use, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

type NewWorkPageProps = {
  params: Promise<{
    id: string
  }>
}

export default function NewWorkPage({
  params,
}: NewWorkPageProps) {
  const { id: exhibitionId } = use(params)

  const router = useRouter()

  const [title, setTitle] = useState("")
  const [artist, setArtist] = useState("")
  const [description, setDescription] = useState("")
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
        "/api/admin/works",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            exhibition_id: exhibitionId,
            title,
            artist: artist || null,
            description,
          }),
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (!response.ok) {
        setError(
          "Não foi possível cadastrar a obra."
        )
        return
      }

      router.push(
        `/admin/exhibitions/${exhibitionId}/works`
      )
      router.refresh()
    } catch {
      setError(
        "Não foi possível cadastrar a obra."
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="admin-page">
      <div className="admin-container admin-form-container">
        <header className="admin-form-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>Nova obra</h1>

            <p>
              Cadastre as informações principais da obra.
              Os recursos de acessibilidade poderão ser
              enviados após o cadastro.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href={`/admin/exhibitions/${exhibitionId}/works`}
          >
            Voltar às obras
          </Link>
        </header>

        <section className="admin-form-card">
          <form
            className="admin-form"
            onSubmit={handleSubmit}
          >
            <div className="admin-field">
              <label htmlFor="title">
                Título
              </label>

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
              <label htmlFor="artist">
                Artista
              </label>

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

            <div className="admin-info-box">
              <strong>
                Recursos de acessibilidade
              </strong>

              <p>
                Após cadastrar a obra, use a opção
                Editar para enviar o áudio, a
                audiodescrição e o vídeo em Libras.
              </p>
            </div>

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
                  : "Cadastrar obra"}
              </button>

              <Link
                className="admin-cancel-link"
                href={`/admin/exhibitions/${exhibitionId}/works`}
              >
                Cancelar
              </Link>
            </div>
          </form>
        </section>
      </div>
    </main>
  )
}