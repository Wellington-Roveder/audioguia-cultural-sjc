import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Link from "next/link";
import DeleteExhibitionButton from "./exhibitions/DeleteExhibitionButton";

type Admin = {
  id: string;
  email: string;
};

type Exhibition = {
  id: string;
  title: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
};

async function getCurrentAdmin(token: string): Promise<Admin | null> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(`${apiUrl}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to validate admin session");
  }

  return response.json();
}

async function getExhibitions(token: string): Promise<Exhibition[]> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(`${apiUrl}/exhibitions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/admin/login");
  }

  if (!response.ok) {
    throw new Error("Failed to load exhibitions");
  }

  return response.json();
}

export default async function AdminPage() {
  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    redirect("/admin/login");
  }

  const admin = await getCurrentAdmin(session.value);

  if (!admin) {
    redirect("/admin/login");
  }

  const exhibitions = await getExhibitions(session.value);

  return (
    <main>
      <h1>Painel administrativo</h1>
      <p>Autenticado como {admin.email}</p>

      <h2>Exposições</h2>
      <p>
        <Link href="/admin/exhibitions/new">
        Nova exposição
        </Link>
      </p>

      {exhibitions.length === 0 ? (
        <p>Nenhuma exposição cadastrada.</p>
      ) : (
        <ul>
          {exhibitions.map((exhibition) => (
            <li key={exhibition.id}>
              <strong>{exhibition.title}</strong>

              {exhibition.description && (
                <p>{exhibition.description}</p>
              )}

              <p>
                Status: {exhibition.is_active ? "Ativa" : "Inativa"}
              </p>
              <p>
                <Link href={`/admin/exhibitions/${exhibition.id}/edit`}>
                 Editar
                </Link>
                
                <DeleteExhibitionButton
                  exhibitionId={exhibition.id}
                  exhibitionTitle={exhibition.title}
                />
                <Link
                href={`/admin/exhibitions/${exhibition.id}/works`}
                >
                  Gerenciar obras
                </Link>
                
                <Link href={`/admin/exhibitions/${exhibition.id}/metrics`}>
                    Ver métricas
                </Link>
              </p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}