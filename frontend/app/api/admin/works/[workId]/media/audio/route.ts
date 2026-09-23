import { cookies } from "next/headers"
import { NextRequest, NextResponse } from "next/server"

export async function POST(
  request: NextRequest,
  context: {
    params: Promise<{ workId: string }>
  }
) {
  const { workId } = await context.params

  const cookieStore = await cookies()
  const session = cookieStore.get("admin_session")

  if (!session) {
    return NextResponse.json(
      { detail: "Unauthorized" },
      { status: 401 }
    )
  }

  const apiUrl = process.env.API_URL

  if (!apiUrl) {
    return NextResponse.json(
      { detail: "API_URL is not configured" },
      { status: 500 }
    )
  }

  const formData = await request.formData()

  const response = await fetch(
    `${apiUrl}/works/${workId}/media/audio`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.value}`,
      },
      body: formData,
    }
  )

  const body = await response.text()

  return new NextResponse(body, {
    status: response.status,
    headers: {
      "Content-Type":
        response.headers.get("content-type") ??
        "application/json",
    },
  })
}