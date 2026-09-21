import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";

type Work = {
  id: string;
  title: string;
};

type ExhibitionMetrics = {
  exhibition_id: string;
  access_count: number;
};

type WorkMetrics = {
  work_id: string;
  access_count: number;
};

type MetricsPageProps = {
  params: Promise<{
    id: string;
  }>;
};

async function authenticatedFetch(
  url: string,
  token: string,
): Promise<Response> {
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/admin/login");
  }

  return response;
}

async function getExhibitionMetrics(
  exhibitionId: string,
  token: string,
): Promise<ExhibitionMetrics> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await authenticatedFetch(
    `${apiUrl}/metrics/exhibitions/${exhibitionId}`,
    token,
  );

  if (!response.ok) {
    throw new Error("Failed to load exhibition metrics");
  }

  return response.json();
}

async function getWorks(
  exhibitionId: string,
  token: string,
): Promise<Work[]> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await authenticatedFetch(
    `${apiUrl}/works/by-exhibition/${exhibitionId}`,
    token,
  );

  if (response.status === 404) {
    return [];
  }

  if (!response.ok) {
    throw new Error("Failed to load works");
  }

  return response.json();
}

async function getWorkMetrics(
  workId: string,
  token: string,
): Promise<WorkMetrics> {
  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await authenticatedFetch(
    `${apiUrl}/metrics/works/${workId}`,
    token,
  );

  if (!response.ok) {
    throw new Error("Failed to load work metrics");
  }

  return response.json();
}

export default async function MetricsPage({
  params,
}: MetricsPageProps) {
  const { id } = await params;

  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    redirect("/admin/login");
  }

  const [exhibitionMetrics, works] = await Promise.all([
    getExhibitionMetrics(id, session.value),
    getWorks(id, session.value),
  ]);

  const workMetrics = await Promise.all(
    works.map(async (work) => {
      const metrics = await getWorkMetrics(
        work.id,
        session.value,
      );

      return {
        ...work,
        access_count: metrics.access_count,
      };
    }),
  );

  return (
    <main>
      <h1>Métricas da exposição</h1>

      <p>
        <Link href="/admin">Voltar ao painel</Link>
      </p>

      <section>
        <h2>Acessos da exposição</h2>
        <p>
          Total de acessos:{" "}
          <strong>{exhibitionMetrics.access_count}</strong>
        </p>
      </section>

      <section>
        <h2>Acessos por obra</h2>

        {workMetrics.length === 0 ? (
          <p>Nenhuma obra cadastrada.</p>
        ) : (
          <ul>
            {workMetrics.map((work) => (
              <li key={work.id}>
                <strong>{work.title}</strong>
                <p>{work.access_count} acessos</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}