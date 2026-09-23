"use client"

import { FormEvent, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function NewExhibitionPage() {
  const router = useRouter()

  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
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
        "/api/admin/exhibitions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title,
            description: description || null,
            start_date: startDate || null,
            end_date: endDate || null,
          }),
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (!response.ok) {
        setError(
          "Não foi possível cadastrar a exposição."
        )
        return
      }

      router.push("/admin")
      router.refresh()
    } catch {
      setError(
        "Não foi possível cadastrar a exposição."
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

            <h1>Nova exposição</h1>

            <p>
              Cadastre uma nova exposição para organizar
              suas obras.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href="/admin"
          >
            Voltar ao painel
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
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                required
              />
            </div>

            <div className="admin-field">
              <label htmlFor="description">
                Descrição
              </label>

              <textarea
                id="description"
                rows={6}
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
              />
            </div>

            <div className="admin-date-grid">
              <div className="admin-field">
                <label htmlFor="start-date">
                  Data de início
                </label>

                <input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(event) =>
                    setStartDate(event.target.value)
                  }
                />
              </div>

              <div className="admin-field">
                <label htmlFor="end-date">
                  Data de término
                </label>

                <input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(event) =>
                    setEndDate(event.target.value)
                  }
                />
              </div>
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
                  : "Cadastrar exposição"}
              </button>

              <Link
                className="admin-cancel-link"
                href="/admin"
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