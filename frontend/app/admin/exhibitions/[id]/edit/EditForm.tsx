"use client"

import { FormEvent, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

type Exhibition = {
  id: string
  title: string
  description: string | null
  start_date: string | null
  end_date: string | null
  is_active: boolean
}

export default function EditForm({
  exhibition,
}: {
  exhibition: Exhibition
}) {
  const router = useRouter()

  const [title, setTitle] = useState(exhibition.title)
  const [description, setDescription] = useState(
    exhibition.description ?? ""
  )
  const [startDate, setStartDate] = useState(
    exhibition.start_date ?? ""
  )
  const [endDate, setEndDate] = useState(
    exhibition.end_date ?? ""
  )
  const [isActive, setIsActive] = useState(
    exhibition.is_active
  )

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
        `/api/admin/exhibitions/${exhibition.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title,
            description: description || null,
            start_date: startDate || null,
            end_date: endDate || null,
            is_active: isActive,
          }),
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (!response.ok) {
        setError(
          "Não foi possível atualizar a exposição."
        )
        return
      }

      router.push("/admin")
      router.refresh()
    } catch {
      setError(
        "Não foi possível atualizar a exposição."
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
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

      <label className="admin-checkbox">
        <input
          type="checkbox"
          checked={isActive}
          onChange={(event) =>
            setIsActive(event.target.checked)
          }
        />

        <span>Exposição ativa</span>
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

        <Link
          className="admin-cancel-link"
          href="/admin"
        >
          Cancelar
        </Link>
      </div>
    </form>
  )
}