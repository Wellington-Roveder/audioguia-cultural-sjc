import { cookies } from "next/headers"
import Link from "next/link"
import { redirect } from "next/navigation"

type Work = {
  id: string
  title: string
}

type ExhibitionMetrics = {
  exhibition_id: string
  access_count: number
}

type WorkMetrics = {
  work_id: string
  access_count: number
}

type MetricsPageProps = {
  params: Promise<{
    id: string
  }>
}

async function authenticatedFetch(
  url: string,
  token: string
): Promise<Response> {
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  })

  if (response.status === 401) {
    redirect("/admin/login")
  }

  return response
}

async function getExhibitionMetrics(
  exhibitionId: string,
  token: string
): Promise<ExhibitionMetrics> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await authenticatedFetch(
    `${apiUrl}/metrics/exhibitions/${exhibitionId}`,
    token
  )

  if (!response.ok) {
    throw new Error(
      "Failed to load exhibition metrics"
    )
  }

  return response.json()
}

async function getWorks(
  exhibitionId: string,
  token: string
): Promise<Work[]> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await authenticatedFetch(
    `${apiUrl}/works/by-exhibition/${exhibitionId}`,
    token
  )

  if (response.status === 404) {
    return []
  }

  if (!response.ok) {
    throw new Error("Failed to load works")
  }

  return response.json()
}

async function getWorkMetrics(
  workId: string,
  token: string
): Promise<WorkMetrics> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await authenticatedFetch(
    `${apiUrl}/metrics/works/${workId}`,
    token
  )

  if (!response.ok) {
    throw new Error("Failed to load work metrics")
  }

  return response.json()
}

export default async function MetricsPage({
  params,
}: MetricsPageProps) {
  const { id } = await params

  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    redirect("/admin/login")
  }

  const [exhibitionMetrics, works] =
    await Promise.all([
      getExhibitionMetrics(id, session.value),
      getWorks(id, session.value),
    ])

  const workMetrics = await Promise.all(
    works.map(async (work) => {
      const metrics = await getWorkMetrics(
        work.id,
        session.value
      )

      return {
        ...work,
        access_count: metrics.access_count,
      }
    })
  )

  return (
    <main className="admin-page">
      <div className="admin-container">
        <header className="admin-form-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>Métricas da exposição</h1>

            <p>
              Acompanhe os acessos à exposição e às
              obras cadastradas.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href="/admin"
          >
            Voltar ao painel
          </Link>
        </header>

        <section className="metrics-summary">
          <p className="metrics-label">
            Total de acessos
          </p>

          <strong className="metrics-total">
            {exhibitionMetrics.access_count}
          </strong>

          <p className="metrics-description">
            acessos registrados nesta exposição
          </p>
        </section>

        <section className="admin-section">
          <div className="admin-section-header">
            <div>
              <h2>Acessos por obra</h2>

              <p>
                Visualize quantos acessos cada obra
                recebeu.
              </p>
            </div>
          </div>

          {workMetrics.length === 0 ? (
            <div className="admin-empty-state">
              <p>Nenhuma obra cadastrada.</p>
            </div>
          ) : (
            <div className="metrics-work-list">
              {workMetrics.map((work) => (
                <article
                  className="metrics-work-card"
                  key={work.id}
                >
                  <div>
                    <h3>{work.title}</h3>

                    <p>Acessos registrados</p>
                  </div>

                  <strong className="metrics-work-count">
                    {work.access_count}
                  </strong>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}