import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";
import DeleteWorkButton from "./DeleteWorkButton";

type Work = {
  id: string;
  exhibition_id: string;
  title: string;
  artist: string | null;
  description: string | null;
  audio_url: string | null;
  audio_description_url: string | null;
  libras_video_url: string | null;
  public_slug: string;
  is_active: boolean;
};

type WorksPageProps = {
  params: Promise<{
    id: string;
  }>;
};

async function getWorks(
  exhibitionId: string,
  token: string,
): Promise<Work[]> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(
    `${apiUrl}/works/by-exhibition/${exhibitionId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (response.status === 401) {
    redirect("/admin/login");
  }

  if (response.status === 404) {
    return [];
  }

  if (!response.ok) {
    throw new Error("Failed to load works");
  }

  return response.json();
}

export default async function WorksPage({
  params,
}: WorksPageProps) {
  const { id } = await params;

  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    redirect("/admin/login");
  }

  const works = await getWorks(id, session.value);

  return (
    <main>
      <h1>Obras da exposição</h1>

      <p>
        <Link href="/admin">Voltar ao painel</Link>
      </p>
      <p>
        <Link href={`/admin/exhibitions/${id}/works/new`}>
            Nova obra
        </Link>
      </p>

      {works.length === 0 ? (
        <p>Nenhuma obra cadastrada.</p>
      ) : (
        <ul>
          {works.map((work) => (
            <li key={work.id}>
              <strong>{work.title}</strong>

              {work.artist && (
                <p>Artista: {work.artist}</p>
              )}

              <p>
                Status: {work.is_active ? "Ativa" : "Inativa"}
              </p>
              <p>
                <Link
                    href={`/admin/exhibitions/${id}/works/${work.id}/edit`}
                >
                    Editar
                </Link>
              </p>
              <DeleteWorkButton
                workId={work.id}
                workTitle={work.title}
               />
              <p>
                <Link
                    href={`/admin/exhibitions/${id}/works/${work.id}/qr`}
                >
                    QR Code
                </Link>
              </p>

            </li>
          ))}
        </ul>
      )}
    </main>
  );
}