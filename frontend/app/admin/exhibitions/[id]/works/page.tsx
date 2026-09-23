import { cookies } from "next/headers"
import Link from "next/link"
import { redirect } from "next/navigation"

import DeleteWorkButton from "./DeleteWorkButton"

type Work = {
  id: string
  exhibition_id: string
  title: string
  artist: string | null
  description: string | null
  audio_url: string | null
  audio_description_url: string | null
  libras_video_url: string | null
  public_slug: string
  is_active: boolean
}

type WorksPageProps = {
  params: Promise<{
    id: string
  }>
}

async function getWorks(
  exhibitionId: string,
  token: string
): Promise<Work[]> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(
    `${apiUrl}/works/by-exhibition/${exhibitionId}`,
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
    return []
  }

  if (!response.ok) {
    throw new Error("Failed to load works")
  }

  return response.json()
}

export default async function WorksPage({
  params,
}: WorksPageProps) {
  const { id } = await params

  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    redirect("/admin/login")
  }

  const works = await getWorks(id, session.value)

  return (
    <main className="admin-page">
      <div className="admin-container">
        <header className="admin-form-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>Obras da exposição</h1>

            <p>
              Gerencie o conteúdo e os recursos de
              acessibilidade das obras.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href="/admin"
          >
            Voltar ao painel
          </Link>
        </header>

        <section className="admin-section">
          <div className="admin-section-header">
            <div>
              <h2>Obras cadastradas</h2>

              <p>
                {works.length === 1
                  ? "1 obra cadastrada."
                  : `${works.length} obras cadastradas.`}
              </p>
            </div>

            <Link
              className="admin-primary-link"
              href={`/admin/exhibitions/${id}/works/new`}
            >
              Nova obra
            </Link>
          </div>

          {works.length === 0 ? (
            <div className="admin-empty-state">
              <p>Nenhuma obra cadastrada.</p>
            </div>
          ) : (
            <div className="work-admin-list">
              {works.map((work) => (
                <article
                  className="work-admin-card"
                  key={work.id}
                >
                  <div className="work-admin-card-header">
                    <div>
                      <h3>{work.title}</h3>

                      {work.artist && (
                        <p className="work-admin-artist">
                          {work.artist}
                        </p>
                      )}
                    </div>

                    <span
                      className={
                        work.is_active
                          ? "status-badge status-active"
                          : "status-badge status-inactive"
                      }
                    >
                      {work.is_active
                        ? "Ativa"
                        : "Inativa"}
                    </span>
                  </div>

                  {work.description && (
                    <p className="work-admin-description">
                      {work.description}
                    </p>
                  )}

                  <div className="work-media-status">
                    <span>
                      Áudio{" "}
                      <strong>
                        {work.audio_url ? "✓" : "—"}
                      </strong>
                    </span>

                    <span>
                      Audiodescrição{" "}
                      <strong>
                        {work.audio_description_url
                          ? "✓"
                          : "—"}
                      </strong>
                    </span>

                    <span>
                      Libras{" "}
                      <strong>
                        {work.libras_video_url
                          ? "✓"
                          : "—"}
                      </strong>
                    </span>
                  </div>

                  <div className="exhibition-actions">
                    <Link
                      href={`/admin/exhibitions/${id}/works/${work.id}/edit`}
                    >
                      Editar
                    </Link>

                    <Link
                      href={`/admin/exhibitions/${id}/works/${work.id}/qr`}
                    >
                      QR Code
                    </Link>

                    <DeleteWorkButton
                      workId={work.id}
                      workTitle={work.title}
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