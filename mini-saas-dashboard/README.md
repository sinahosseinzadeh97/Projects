# Mini SaaS Projects Dashboard

A small full-stack dashboard for managing SaaS projects.  
Built as a solution to the **“Full-Stack Developer Task – Mini SaaS Dashboard”** to demonstrate skills in **Next.js**, **Prisma**, **PostgreSQL (Supabase)**, **Clerk**, and **TypeScript**.

---

## 🔗 Links

- **Live demo (Vercel)**  
  https://mini-saas-dashboard-ten.vercel.app/dashboard
- **GitHub repository**  
  https://github.com/sinahosseinzadeh97/Projects.git  
  > This dashboard lives in the `mini-saas-dashboard` folder of the repo.

---

## 🎯 Task Context – Full-Stack Developer Task

This project implements the following assignment:

> **Full-Stack Developer Task – Mini SaaS Dashboard**  
> Create a simple web dashboard where you can list, filter, search, add and edit projects.  
> Each project needs at least these fields:
> - Status (e.g. “active”, “on hold”, “completed”)
> - Deadline
> - Assigned team member
> - Budget
>
> **Frontend requirements:**
> - Utilize React or Next.js with a CSS framework like Tailwind
> - Implement a responsive design featuring a table view with filtering and search capabilities by project status
> - Include a modal form to add or edit project details
>
> **Backend requirements:**
> - Develop using Node.js with Express or Next.js API routes
> - Store data in PostgreSQL or MongoDB
> - Implement RESTful or GraphQL endpoints
> - Data seeding:
>   - You may generate your own dummy data, or
>   - Fetch from a free public API (e.g. JSONPlaceholder, Mockaroo) and seed your database
> - Endpoints: Implement CRUD via REST or GraphQL
>
> **Bonus points:**
> - Implement authentication (e.g., JWT or session-based)
> - Use GitHub for version control and share commit history
> - Provide a brief README with setup and usage instructions
> - Bonus: Deployment, containerization, and any additional features beyond the requirements

This repository is my implementation of that task.

---

## ✅ Features

- 🔐 **Authentication (Bonus)**  
  - Implemented using **Clerk** (session-based authentication)  
  - Login page at `/login` using `<SignIn />` from `@clerk/nextjs`  
  - Protected routes:
    - `/dashboard`
    - `/api/projects/*`
  - Unauthenticated behavior:
    - API calls → `401 Unauthorized` JSON response
    - Pages → redirect to `/login?redirectTo=/original/path`

- 📊 **Projects dashboard**
  - Responsive table listing all projects
  - Columns: **Name**, **Status**, **Deadline**, **Assigned team member**, **Budget**
  - Status badges: **Active**, **On hold**, **Completed**
  - Sorted by creation date (newest first)

- 🔎 **Filtering & search**
  - Filter by project status (Active / On hold / Completed)
  - Client-side search by **project name** and **assignee**
  - Layout is responsive on desktop and smaller screens

- ✏️ **Project CRUD**
  - Create new projects via a modal form
  - Edit existing projects using the same modal
  - Delete projects with confirmation
  - All operations wired to **RESTful** API endpoints under `/api/projects`

- 🗄 **Persistent storage**
  - **PostgreSQL (Supabase)** as the main database
  - **Prisma ORM** for:
    - schema definition
    - migrations
    - type-safe database access

- ☁️ **Deployment & DevOps (Bonus)**
  - Deployed on **Vercel**
  - Includes a production-ready **multi-stage Dockerfile**
  - Uses environment variables for DB & auth configuration

---

## 🧱 Tech Stack

**Frontend**

- [Next.js](https://nextjs.org/) (App Router)
- React
- TypeScript
- Tailwind CSS (`src/app/globals.css`)
- Geist font via `next/font`

**Backend**

- Next.js Route Handlers (`src/app/api/**`)
- Node.js runtime
- Prisma ORM
- PostgreSQL (Supabase)

**Authentication**

- [Clerk](https://clerk.com/) via `@clerk/nextjs`
- `ClerkProvider` configured in `src/app/layout.tsx`
- `clerkMiddleware` in `middleware.ts` to protect:
  - `/dashboard`
  - `/api/projects/*`

**Tooling & Deployment**

- Vercel
- Docker
- ESLint
- TypeScript

---

## 🗂 Project Structure (Relevant Files)

```text
.
├── Dockerfile
├── prisma
│   ├── dev.db                # Legacy SQLite file (not used with Supabase)
│   ├── migrations/           # Prisma migrations
│   └── schema.prisma         # PostgreSQL schema (Project model + enums)
├── prisma.config.ts          # Prisma config (reads DATABASE_URL from env)
├── public
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
├── src
│   └── app
│       ├── api
│       │   ├── auth
│       │   │   ├── login/route.ts    # Legacy/simple login (optional)
│       │   │   └── logout/route.ts   # Legacy/simple logout (optional)
│       │   └── projects
│       │       ├── route.ts          # GET/POST /api/projects
│       │       └── [id]/route.ts     # GET/PUT/DELETE /api/projects/:id
│       ├── components
│       │   ├── ProjectFilters.tsx    # Status filter + search
│       │   ├── ProjectModal.tsx      # Modal for create/edit
│       │   └── ProjectTable.tsx      # Table UI
│       ├── dashboard
│       │   └── page.tsx              # Main dashboard page (protected)
│       ├── lib
│       │   └── prisma.ts             # Prisma client singleton
│       ├── login
│       │   └── page.tsx              # Login page (Clerk <SignIn />)
│       ├── types
│       │   └── project.ts            # Shared Project types/interfaces
│       ├── globals.css               # Tailwind/global styles
│       ├── layout.tsx                # Root layout + ClerkProvider
│       └── page.tsx                  # Redirects "/" → "/login"
├── middleware.ts                     # Clerk-based route protection
├── package.json
├── tsconfig.json
├── postcss.config.mjs
└── README.md
