# Mini SaaS Projects Dashboard

A small full-stack dashboard for managing SaaS projects.  
Built as an interview task to demonstrate skills in **Next.js**, **Prisma**, and **TypeScript**.

---

## Features

- 🔐 **Simple authentication**
  - Email + password from environment variables
  - Cookie-based auth with middleware protection
- 📊 **Projects dashboard**
  - List all projects in a responsive table
  - Status badges: **Active**, **On hold**, **Completed**
  - Sort by creation date (newest first)
- 🔎 **Filtering & search**
  - Filter by project status
  - Search by project name and assignee (client-side)
- ✏️ **CRUD operations**
  - Create new projects via a modal form
  - Edit existing projects via the same form
  - Delete projects with confirmation
- 🗄 **Persistent storage**
  - Prisma ORM
  - SQLite for local development (can be swapped to PostgreSQL easily)

---

## Tech Stack

**Frontend**

- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS (via `globals.css`)

**Backend**

- Next.js Route Handlers (`/app/api`)
- Prisma ORM
- SQLite database (file-based, local dev)

**Auth**

- Custom, minimal auth:
  - `POST /api/auth/login` sets an HTTP-only cookie
  - `POST /api/auth/logout` clears the cookie
  - `middleware.ts` protects `/dashboard` and `/api/projects/*`

---

## Project Structure

High-level structure (relevant parts):

```text
.
├── prisma
│   ├── dev.db               # SQLite database file (local dev)
│   ├── migrations/          # Prisma migrations
│   └── schema.prisma        # Prisma schema (Project model + enums)
├── src
│   └── app
│       ├── api
│       │   ├── auth
│       │   │   ├── login/route.ts   # POST /api/auth/login
│       │   │   └── logout/route.ts  # POST /api/auth/logout
│       │   ├── projects
│       │   │   ├── route.ts         # GET/POST /api/projects
│       │   │   └── [id]/route.ts    # GET/PUT/DELETE /api/projects/:id
│       ├── components
│       │   ├── ProjectFilters.tsx   # Status filter + search box
│       │   ├── ProjectModal.tsx     # Modal for create/edit
│       │   └── ProjectTable.tsx     # Table UI
│       ├── dashboard
│       │   └── page.tsx             # Main dashboard page (protected)
│       ├── login
│       │   └── page.tsx             # Login form (client component)
│       ├── types
│       │   └── project.ts           # Shared types/interfaces
│       ├── layout.tsx               # Root layout
│       └── page.tsx                 # Redirects "/" → "/login"
├── middleware.ts                    # Protects /dashboard and /api/projects/*
├── package.json
├── tsconfig.json
└── README.md
