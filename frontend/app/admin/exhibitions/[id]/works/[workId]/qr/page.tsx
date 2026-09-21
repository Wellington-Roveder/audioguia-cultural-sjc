import Image from "next/image";
import Link from "next/link";

type QrPageProps = {
  params: Promise<{
    id: string;
    workId: string;
  }>;
};

export default async function QrPage({
  params,
}: QrPageProps) {
  const { id: exhibitionId, workId } = await params;

  const qrUrl = `/api/admin/works/${workId}/qr`;

  return (
    <main>
      <h1>QR Code da obra</h1>

      <div>
        <Image
          src={qrUrl}
          alt="QR Code de acesso à obra"
          width={300}
          height={300}
          unoptimized
        />
      </div>

      <p>
        <a href={qrUrl} download>
          Baixar QR Code
        </a>
      </p>

      <p>
        <Link
          href={`/admin/exhibitions/${exhibitionId}/works`}
        >
          Voltar às obras
        </Link>
      </p>
    </main>
  );
}