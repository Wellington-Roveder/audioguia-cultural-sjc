import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{
    workId: string;
  }>;
};

export async function GET(
  _request: Request,
  context: RouteContext,
) {
  const { workId } = await context.params;

  const cookieStore = await cookies();
  const session = cookieStore.get("admin_session");

  if (!session) {
    return NextResponse.json(
      { detail: "Unauthorized" },
      { status: 401 },
    );
  }

  const apiUrl = process.env.API_URL;

  if (!apiUrl) {
    return NextResponse.json(
      { detail: "API_URL is not configured" },
      { status: 500 },
    );
  }

  const response = await fetch(
    `${apiUrl}/metrics/works/${workId}`,
    {
      headers: {
        Authorization: `Bearer ${session.value}`,
      },
      cache: "no-store",
    },
  );

  const data = await response.json();

  return NextResponse.json(data, {
    status: response.status,
  });
}