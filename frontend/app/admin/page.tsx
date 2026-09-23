import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import Link from "next/link"

import DeleteExhibitionButton from "./exhibitions/DeleteExhibitionButton"
import LogoutButton from "./LogoutButton"

type Admin = {
  id: string
  email: string
}

type Exhibition = {
  id: string
  title: string
  description: string | null
  start_date: string | null
  end_date: string | null
  is_active: boolean
}

async function getCurrentAdmin(
  token: string
): Promise<Admin | null> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(`${apiUrl}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  })

  if (response.status === 401) {
    return null
  }

  if (!response.ok) {
    throw new Error("Failed to validate admin session")
  }

  return response.json()
}

async function getExhibitions(
  token: string
): Promise<Exhibition[]> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(`${apiUrl}/exhibitions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  })

  if (response.status === 401) {
    redirect("/admin/login")
  }

  if (!response.ok) {
    throw new Error("Failed to load exhibitions")
  }

  return response.json()
}

export default async function AdminPage() {
  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    redirect("/admin/login")
  }

  const admin = await getCurrentAdmin(session.value)

  if (!admin) {
    redirect("/admin/login")
  }

  const exhibitions = await getExhibitions(session.value)

  return (
    <main className="admin-page">
      <div className="admin-container">
        <header className="admin-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>Painel administrativo</h1>

            <p className="admin-user">
              Autenticado como {admin.email}
            </p>
          </div>

          <LogoutButton />
        </header>

        <section className="admin-section">
          <div className="admin-section-header">
            <div>
              <h2>Exposições</h2>
              <p>
                Gerencie as exposições e seus conteúdos.
              </p>
            </div>

            <Link
              className="admin-primary-link"
              href="/admin/exhibitions/new"
            >
              Nova exposição
            </Link>
          </div>

          {exhibitions.length === 0 ? (
            <div className="admin-empty-state">
              <p>Nenhuma exposição cadastrada.</p>
            </div>
          ) : (
            <div className="exhibition-list">
              {exhibitions.map((exhibition) => (
                <article
                  className="exhibition-card"
                  key={exhibition.id}
                >
                  <div className="exhibition-card-header">
                    <h3>{exhibition.title}</h3>

                    <span
                      className={
                        exhibition.is_active
                          ? "status-badge status-active"
                          : "status-badge status-inactive"
                      }
                    >
                      {exhibition.is_active
                        ? "Ativa"
                        : "Inativa"}
                    </span>
                  </div>

                  {exhibition.description && (
                    <p className="exhibition-description">
                      {exhibition.description}
                    </p>
                  )}

                  {(exhibition.start_date ||
                    exhibition.end_date) && (
                    <p className="exhibition-dates">
                      {exhibition.start_date &&
                        `Início: ${exhibition.start_date}`}

                      {exhibition.start_date &&
                        exhibition.end_date &&
                        " • "}

                      {exhibition.end_date &&
                        `Término: ${exhibition.end_date}`}
                    </p>
                  )}

                  <div className="exhibition-actions">
                    <Link
                      href={`/admin/exhibitions/${exhibition.id}/works`}
                    >
                      Gerenciar obras
                    </Link>

                    <Link
                      href={`/admin/exhibitions/${exhibition.id}/metrics`}
                    >
                      Ver métricas
                    </Link>

                    <Link
                      href={`/admin/exhibitions/${exhibition.id}/edit`}
                    >
                      Editar
                    </Link>

                    <DeleteExhibitionButton
                      exhibitionId={exhibition.id}
                      exhibitionTitle={exhibition.title}
                    />
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}