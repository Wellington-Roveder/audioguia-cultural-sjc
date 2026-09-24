import AccessTracker from "./AccessTracker"

type PublicWork = {
  title: string
  artist: string | null
  description: string
  audio_url: string | null
  audio_description_url: string | null
  libras_video_url: string | null
}

async function getPublicWork(
  publicSlug: string
): Promise<PublicWork | null> {
  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    throw new Error("API_URL is not configured")
  }

  const response = await fetch(
    `${apiUrl}/public/works/${publicSlug}`,
    {
      cache: "no-store",
    }
  )

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    throw new Error("Failed to fetch work")
  }

  return response.json()
}

export default async function PublicWorkPage({
  params,
}: {
  params: Promise<{ public_slug: string }>
}) {
  const { public_slug } = await params

  const work = await getPublicWork(public_slug)

  if (!work) {
    return (
      <main className="work-page">
        <section className="work-card">
          <p className="work-eyebrow">
            Audioguia Cultural SJC
          </p>

          <h1>Obra não encontrada</h1>

          <p className="work-description">
            Esta obra não está disponível no momento.
          </p>
        </section>
      </main>
    )
  }

  const publicApiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!publicApiUrl) {
     new Error("NEXT_PUBLIC_API_URL is not configured");
  }

  const audioUrl =
    `${publicApiUrl}/public/works/${public_slug}/media/audio`;

  const audioDescriptionUrl =
    `${publicApiUrl}/public/works/${public_slug}/media/audio-description`;

  const librasVideoUrl =
    `${publicApiUrl}/public/works/${public_slug}/media/libras`;

  return (
    <main className="work-page">
      <AccessTracker publicSlug={public_slug} />

      <article className="work-card">
        <header className="work-header">
          <p className="work-eyebrow">
            Audioguia Cultural SJC
          </p>

          <h1>{work.title}</h1>

          {work.artist && (
            <p className="work-artist">
              {work.artist}
            </p>
          )}
        </header>

        <section className="work-content">
          <p className="work-description">
            {work.description}
          </p>
        </section>

        {(work.audio_url ||
          work.audio_description_url ||
          work.libras_video_url) && (
          <section
            className="work-accessibility"
            aria-labelledby="accessibility-title"
          >
            <h2 id="accessibility-title">
              Recursos disponíveis
            </h2>

            {work.audio_url && (
              <div className="media-block">
                <h3>Ouvir conteúdo</h3>

                <audio
                  controls
                  preload="metadata"
                  src={audioUrl}
                >
                  Seu navegador não suporta áudio.
                </audio>
              </div>
            )}

            {work.audio_description_url && (
              <div className="media-block">
                <h3>Audiodescrição</h3>

                <audio
                  controls
                  preload="metadata"
                  src={audioDescriptionUrl}
                >
                  Seu navegador não suporta áudio.
                </audio>
              </div>
            )}

            {work.libras_video_url && (
              <div className="media-block">
                <h3>Vídeo em Libras</h3>

                <video
                  controls
                  preload="metadata"
                  src={librasVideoUrl}
                >
                  Seu navegador não suporta vídeo.
                </video>
              </div>
            )}
          </section>
        )}

        <footer className="work-footer">
          <p>
            Conteúdo cultural digital para apoio à visita.
          </p>
        </footer>
      </article>
    </main>
  )
}