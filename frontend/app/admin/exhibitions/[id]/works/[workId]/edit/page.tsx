import { cookies } from "next/headers"
import Link from "next/link"
import { redirect } from "next/navigation"

import EditForm from "@/app/admin/exhibitions/[id]/works/[workId]/edit/EditForm"

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

type EditWorkPageProps = {
  params: Promise<{
    id: string
    workId: string
  }>
}

async function getWork(
  workId: string,
  token: string
): Promise<Work | null> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(
    `${apiUrl}/works/${workId}`,
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
    throw new Error("Failed to load work")
  }

  return response.json()
}

export default async function EditWorkPage({
  params,
}: EditWorkPageProps) {
  const { id: exhibitionId, workId } = await params

  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    redirect("/admin/login")
  }

  const work = await getWork(
    workId,
    session.value
  )

  if (!work) {
    return (
      <main className="admin-page">
        <div className="admin-container admin-form-container">
          <section className="admin-form-card">
            <h1>Obra não encontrada</h1>

            <Link
              className="admin-back-link"
              href={`/admin/exhibitions/${exhibitionId}/works`}
            >
              Voltar às obras
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

            <h1>Editar obra</h1>

            <p>
              Atualize os dados da obra e gerencie seus
              recursos de acessibilidade.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href={`/admin/exhibitions/${exhibitionId}/works`}
          >
            Voltar às obras
          </Link>
        </header>

        <EditForm
          work={work}
          exhibitionId={exhibitionId}
        />
      </div>
    </main>
  )
}