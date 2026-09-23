import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import Link from "next/link"

import EditForm from "./EditForm"

type Exhibition = {
  id: string
  title: string
  description: string | null
  start_date: string | null
  end_date: string | null
  is_active: boolean
}

type EditExhibitionPageProps = {
  params: Promise<{
    id: string
  }>
}

async function getExhibition(
  id: string,
  token: string
): Promise<Exhibition | null> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(
    `${apiUrl}/exhibitions/${id}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }
  )

  if (response.status === 401) {
    redirect("/admin/login")
  }

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    throw new Error("Failed to load exhibition")
  }

  return response.json()
}

export default async function EditExhibitionPage({
  params,
}: EditExhibitionPageProps) {
  const { id } = await params

  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    redirect("/admin/login")
  }

  const exhibition = await getExhibition(
    id,
    session.value
  )

  if (!exhibition) {
    return (
      <main className="admin-page">
        <div className="admin-container">
          <section className="admin-form-card">
            <h1>Exposição não encontrada</h1>

            <Link
              className="admin-back-link"
              href="/admin"
            >
              Voltar ao painel
            </Link>
          </section>
        </div>
      </main>
    )
  }

  return (
    <main className="admin-page">
      <div className="admin-container admin-form-container">
        <header className="admin-form-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>Editar exposição</h1>

            <p>
              Atualize as informações da exposição.
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
          <EditForm exhibition={exhibition} />
        </section>
      </div>
    </main>
  )
}