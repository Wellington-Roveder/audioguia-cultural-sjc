"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"

type DeleteExhibitionButtonProps = {
  exhibitionId: string
  exhibitionTitle: string
}

export default function DeleteExhibitionButton({
  exhibitionId,
  exhibitionTitle,
}: DeleteExhibitionButtonProps) {
  const router = useRouter()

  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState("")

  async function handleDelete() {
    const confirmed = window.confirm(
      `Deseja realmente excluir a exposição "${exhibitionTitle}"?`
    )

    if (!confirmed) {
      return
    }

    setDeleting(true)
    setError("")

    try {
      const response = await fetch(
        `/api/admin/exhibitions/${exhibitionId}`,
        {
          method: "DELETE",
        }
      )

      if (response.status === 401) {
        router.push("/admin/login")
        return
      }

      if (!response.ok) {
        setError("Não foi possível excluir a exposição.")
        return
      }

      router.refresh()
    } catch {
      setError("Não foi possível excluir a exposição.")
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="admin-delete-action">
      <button
        className="admin-delete-button"
        type="button"
        onClick={handleDelete}
        disabled={deleting}
      >
        {deleting ? "Excluindo..." : "Excluir"}
      </button>

      {error && (
        <p className="admin-action-error" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}