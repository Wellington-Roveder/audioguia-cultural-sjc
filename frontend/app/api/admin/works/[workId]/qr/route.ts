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
    `${apiUrl}/works/${workId}/qr`,
    {
      headers: {
        Authorization: `Bearer ${session.value}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    return NextResponse.json(
      { detail: "Failed to load QR code" },
      { status: response.status },
    );
  }

  const qrCode = await response.arrayBuffer();

  return new Response(qrCode, {
    status: 200,
    headers: {
      "Content-Type":
        response.headers.get("content-type") ?? "image/png",
      "Cache-Control": "no-store",
    },
  });
}