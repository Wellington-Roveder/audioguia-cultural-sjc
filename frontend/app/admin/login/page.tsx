"use client"

import { FormEvent, useState } from "react"
import { useRouter } from "next/navigation"

export default function AdminLoginPage() {
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    setError("")
    setLoading(true)

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (!response.ok) {
        setError("E-mail ou senha inválidos.")
        return
      }

      router.push("/admin")
      router.refresh()
    } catch {
      setError(
        "Não foi possível realizar o login."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <header className="login-header">
          <p className="admin-eyebrow">
            Audioguia Cultural SJC
          </p>

          <h1>Administração</h1>

          <p>
            Entre com suas credenciais para acessar
            o painel administrativo.
          </p>
        </header>

        <form
          className="admin-form"
          onSubmit={handleSubmit}
        >
          <div className="admin-field">
            <label htmlFor="email">
              E-mail
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />
          </div>

          <div className="admin-field">
            <label htmlFor="password">
              Senha
            </label>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />
          </div>

          {error && (
            <p
              className="admin-form-error"
              role="alert"
            >
              {error}
            </p>
          )}

          <button
            className="admin-submit-button login-button"
            type="submit"
            disabled={loading}
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  )
}