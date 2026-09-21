import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({
    authenticated: false,
  });

  response.cookies.set("admin_session", "", {
    httpOnly: true,
    secure: process.env.COOKIE_SECURE !== "false",
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });

  return response;
}