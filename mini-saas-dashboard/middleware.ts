// middleware.ts

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { clerkMiddleware } from "@clerk/nextjs/server";

// Custom Clerk middleware to protect /dashboard and /api/projects/*
export default clerkMiddleware(async (auth, req: NextRequest) => {
  const pathname = req.nextUrl.pathname;

  const isApiRoute = pathname.startsWith("/api/");
  const isProjectsApi = pathname.startsWith("/api/projects");
  const isDashboardPage = pathname.startsWith("/dashboard");

  // Only protect these routes
  const isProtectedRoute = isDashboardPage || isProjectsApi;

  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  // get auth state from Clerk (async)
  const { userId } = await auth();

  const isAuthenticated = !!userId;

  if (!isAuthenticated) {
    // For API routes → return 401 JSON
    if (isApiRoute) {
      return new NextResponse(
        JSON.stringify({ message: "Unauthorized" }),
        {
          status: 401,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // For pages → redirect to /login with redirectTo param
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // User is authenticated → allow the request
  return NextResponse.next();
});

// Run Clerk middleware on all routes, but we only "protect" some inside
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
