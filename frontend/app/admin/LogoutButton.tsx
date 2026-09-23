"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

export default function LogoutButton() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  async function handleLogout() {
    setLoading(true)

    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
      })

      if (!response.ok) {
        return
      }

      router.replace("/admin/login")
      router.refresh()
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      className="admin-logout-button"
      type="button"
      onClick={handleLogout}
      disabled={loading}
    >
      {loading ? "Saindo..." : "Sair"}
    </button>
  )
}