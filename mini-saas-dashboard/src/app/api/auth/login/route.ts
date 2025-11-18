// src/app/api/auth/login/route.ts

import { NextRequest, NextResponse } from "next/server";

const ADMIN_EMAIL = process.env.ADMIN_EMAIL;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const AUTH_COOKIE_NAME = process.env.AUTH_COOKIE_NAME ?? "mini_saas_auth";

export async function POST(request: NextRequest) {
  // 1) Check auth env vars
  if (!ADMIN_EMAIL || !ADMIN_PASSWORD || !AUTH_TOKEN) {
    console.error("Auth environment variables are not configured.");
    return NextResponse.json(
      { message: "Auth environment variables are not configured." },
      { status: 500 }
    );
  }

  // 2) Read body
  let body: { email?: string; password?: string };
  try {
    body = await request.json();
  } catch (error) {
    console.error("Invalid JSON body:", error);
    return NextResponse.json(
      { message: "Invalid request body" },
      { status: 400 }
    );
  }

  const { email, password } = body;

  if (!email || !password) {
    return NextResponse.json(
      { message: "Email and password are required" },
      { status: 400 }
    );
  }

  // 3) Compare with env credentials
  const isValid =
    email === ADMIN_EMAIL &&
    password === ADMIN_PASSWORD;

  if (!isValid) {
    return NextResponse.json(
      { message: "Invalid credentials." },
      { status: 401 }
    );
  }

  // 4) Set auth cookie
  const response = NextResponse.json(
    { message: "Logged in successfully" },
    { status: 200 }
  );

  response.cookies.set(AUTH_COOKIE_NAME, AUTH_TOKEN, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
  });

  return response;
}
