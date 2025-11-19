// src/app/api/projects/route.ts
export const runtime = "nodejs";
import { NextResponse } from "next/server";
import { prisma } from "@/app/lib/prisma";
import { ProjectStatus } from "@prisma/client";

// GET /api/projects
export async function GET() {
  try {
    // Fetch all projects ordered by creation date (newest first)
    const projects = await prisma.project.findMany({
      orderBy: {
        createdAt: "desc",
      },
    });

    return NextResponse.json(projects, { status: 200 });
  } catch (error) {
    console.error("GET /api/projects error:", error);
    return NextResponse.json(
      { message: "Failed to fetch projects" },
      { status: 500 }
    );
  }
}

// POST /api/projects
export async function POST(request: Request) {
  try {
    const body = await request.json();

    const { name, status, deadline, assignedTo, budget } = body;

    // Basic validation
    if (!name || !status || !deadline || !assignedTo || budget === undefined) {
      return NextResponse.json(
        { message: "Missing required fields" },
        { status: 400 }
      );
    }

    if (!Object.values(ProjectStatus).includes(status as ProjectStatus)) {
      return NextResponse.json(
        { message: "Invalid status value" },
        { status: 400 }
      );
    }

    const parsedDeadline = new Date(deadline);
    if (isNaN(parsedDeadline.getTime())) {
      return NextResponse.json(
        { message: "Invalid deadline date" },
        { status: 400 }
      );
    }

    const parsedBudget = Number(budget);
    if (isNaN(parsedBudget)) {
      return NextResponse.json(
        { message: "Invalid budget" },
        { status: 400 }
      );
    }

    const project = await prisma.project.create({
      data: {
        name,
        status,
        deadline: parsedDeadline,
        assignedTo,
        budget: parsedBudget,
      },
    });

    return NextResponse.json(project, { status: 201 });
  } catch (error) {
    console.error("POST /api/projects error:", error);
    return NextResponse.json(
      { message: "Failed to create project" },
      { status: 500 }
    );
  }
}
