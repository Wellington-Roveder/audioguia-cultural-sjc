import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import EditForm from "./EditForm";

type Exhibition = {
  id: string;
  title: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
};

type EditExhibitionPageProps = {
  params: Promise<{
    id: string;
  }>;
};

async function getExhibition(
  id: string,
  token: string,
): Promise<Exhibition | null> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(
    `${apiUrl}/exhibitions/${id}`,
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
    throw new Error("Failed to load exhibition");
  }

  return response.json();
}

export default async function EditExhibitionPage({
  params,
}: EditExhibitionPageProps) {
  const { id } = await params;

  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    redirect("/admin/login");
  }

  const exhibition = await getExhibition(
    id,
    session.value,
  );

  if (!exhibition) {
    return (
      <main>
        <h1>Exposição não encontrada</h1>
      </main>
    );
  }

  return (
    <main>
      <h1>Editar exposição</h1>
      <EditForm exhibition={exhibition} />
      <p>
        <strong>Título:</strong> {exhibition.title}
      </p>

      <p>
        <strong>Descrição:</strong>{" "}
        {exhibition.description ?? "Sem descrição"}
      </p>

      <p>
        <strong>Data de início:</strong>{" "}
        {exhibition.start_date ?? "Não informada"}
      </p>

      <p>
        <strong>Data de término:</strong>{" "}
        {exhibition.end_date ?? "Não informada"}
      </p>

      <p>
        <strong>Status:</strong>{" "}
        {exhibition.is_active ? "Ativa" : "Inativa"}
      </p>
    </main>
  );
}