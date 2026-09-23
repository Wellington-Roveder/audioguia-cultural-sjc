import Link from "next/link"

import QrDisplay from "./QrDisplay"

type QrPageProps = {
  params: Promise<{
    id: string
    workId: string
  }>
}

export default async function QrPage({
  params,
}: QrPageProps) {
  const { id: exhibitionId, workId } = await params

  const qrUrl = `/api/admin/works/${workId}/qr`

  return (
    <main className="admin-page">
      <div className="admin-container">
        <header className="admin-form-header">
          <div>
            <p className="admin-eyebrow">
              Audioguia Cultural SJC
            </p>

            <h1>QR Code da obra</h1>

            <p>
              Exiba o QR Code em uma tela ou faça
              o download para impressão.
            </p>
          </div>

          <Link
            className="admin-back-link"
            href={`/admin/exhibitions/${exhibitionId}/works`}
          >
            Voltar às obras
          </Link>
        </header>

        <QrDisplay
          qrUrl={qrUrl}
          workId={workId}
        />
      </div>
    </main>
  )
}