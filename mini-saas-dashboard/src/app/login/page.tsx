// src/app/login/page.tsx
"use client";

import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="rounded-2xl bg-slate-900/70 p-6 shadow-xl border border-slate-800">
        {/* Tell Clerk to redirect to /dashboard after successful sign-in */}
        <SignIn redirectUrl="/dashboard" />
      </div>
    </main>
  );
}
