import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";
import EditForm from "@/app/admin/exhibitions/[id]/works/[workId]/edit/EditForm";

type Work = {
  id: string;
  exhibition_id: string;
  title: string;
  artist: string | null;
  description: string;
  audio_url: string | null;
  audio_description_url: string | null;
  libras_video_url: string | null;
  public_slug: string;
  is_active: boolean;
};

type EditWorkPageProps = {
  params: Promise<{
    id: string;
    workId: string;
  }>;
};

async function getWork(
  workId: string,
  token: string,
): Promise<Work | null> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(
    `${apiUrl}/works/${workId}`,
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
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to load work");
  }

  return response.json();
}

export default async function EditWorkPage({
  params,
}: EditWorkPageProps) {
  const { id: exhibitionId, workId } = await params;

  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    redirect("/admin/login");
  }

  const work = await getWork(
    workId,
    session.value,
  );

  if (!work) {
    return (
      <main>
        <h1>Obra não encontrada</h1>

        <Link
          href={`/admin/exhibitions/${exhibitionId}/works`}
        >
          Voltar às obras
        </Link>
      </main>
    );
  }

  return (
  <main>
    <h1>Editar obra</h1>

    <EditForm
      work={work}
      exhibitionId={exhibitionId}
    />

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