"use client"

import Image from "next/image"
import { useRef } from "react"

type QrDisplayProps = {
  qrUrl: string
  workId: string
}

export default function QrDisplay({
  qrUrl,
  workId,
}: QrDisplayProps) {
  const displayRef = useRef<HTMLDivElement>(null)

  async function handleFullscreen() {
    if (!displayRef.current) {
      return
    }

    try {
      await displayRef.current.requestFullscreen()
    } catch {
      // O navegador pode bloquear fullscreen.
    }
  }

  return (
    <section className="qr-admin-card">
      <div
        ref={displayRef}
        className="qr-display"
      >
        <div className="qr-display-content">
          <p className="qr-display-eyebrow">
            Audioguia Cultural SJC
          </p>

          <Image
            className="qr-image"
            src={qrUrl}
            alt="QR Code de acesso à obra"
            width={500}
            height={500}
            unoptimized
            priority
          />

          <p className="qr-instruction">
            Aponte a câmera do celular para acessar
            o conteúdo da obra.
          </p>
        </div>
      </div>

      <div className="qr-actions">
        <button
          className="admin-submit-button"
          type="button"
          onClick={handleFullscreen}
        >
          Exibir em tela cheia
        </button>

        <a
          className="admin-secondary-button"
          href={qrUrl}
          download={`qr-${workId}.png`}
        >
          Baixar QR Code
        </a>
      </div>
    </section>
  )
}