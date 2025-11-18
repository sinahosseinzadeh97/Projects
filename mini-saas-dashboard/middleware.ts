// middleware.ts

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getAuth } from "@clerk/nextjs/server";

// Protect /dashboard page and /api/projects routes using Clerk
export function middleware(request: NextRequest) {
  const { userId } = getAuth(request); // Get auth state from Clerk

  const isApiRoute = request.nextUrl.pathname.startsWith("/api/");
  const isProjectsApi = request.nextUrl.pathname.startsWith("/api/projects");
  const isDashboardPage = request.nextUrl.pathname.startsWith("/dashboard");

  // Only protect these routes (same as the previous custom middleware)
  const isProtectedRoute = isDashboardPage || isProjectsApi;

  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  const isAuthenticated = !!userId;

  if (!isAuthenticated) {
    // For API routes → return 401 JSON
    if (isApiRoute) {
      return NextResponse.json(
        { message: "Unauthorized" },
        { status: 401 }
      );
    }

    // For pages → redirect to /login with redirectTo param
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirectTo", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // User is authenticated → allow the request
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard", "/api/projects/:path*"],
};
