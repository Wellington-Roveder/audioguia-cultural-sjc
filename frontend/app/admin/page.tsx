import { cookies } from "next/headers";
import { redirect } from "next/navigation";

type Admin = {
  id: string;
  email: string;
};

async function getCurrentAdmin(token: string): Promise<Admin | null> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(`${apiUrl}/auth/me`, {
    method: "GET",
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

  return (
    <main>
      <h1>Painel administrativo</h1>
      <p>Sessão autenticada.</p>
      <p>{admin.email}</p>
    </main>
  );
}