"use client"

import { useEffect } from "react"

type AccessTrackerProps = {
  publicSlug: string
}

export default function AccessTracker({
  publicSlug,
}: AccessTrackerProps) {
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    if (!apiUrl) {
      console.error("NEXT_PUBLIC_API_URL is not configured")
      return
    }

    const storageKey = `audioguia:work:${publicSlug}:access`

    const alreadyRegistered = localStorage.getItem(storageKey)

    if (alreadyRegistered) {
      return
    }

    async function registerAccess() {
      try {
        const response = await fetch(
          `${apiUrl}/public/works/${publicSlug}/access`,
          {
            method: "POST",
          }
        )

        if (response.status === 204) {
          localStorage.setItem(storageKey, "1")
        }
      } catch {
        // Não bloqueia a experiência do visitante
        // caso o registro de métricas falhe.
      }
    }

    registerAccess()
  }, [publicSlug])

  return null
}