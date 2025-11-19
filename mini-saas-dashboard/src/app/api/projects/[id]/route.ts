// src/app/api/projects/[id]/route.ts
export const runtime = "nodejs";

import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/app/lib/prisma";
import { ProjectStatus } from "@prisma/client";

// In Next 16, context.params is typed as a Promise<{ id: string }>
type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};

// GET /api/projects/:id
export async function GET(_request: NextRequest, { params }: RouteContext) {
  const { id } = await params;

  try {
    // Use findMany to avoid errors and then pick the first match
    const projects = await prisma.project.findMany({
      where: { id },
    });

    const project = projects[0];

    if (!project) {
      return NextResponse.json(
        { message: "Project not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(project, { status: 200 });
  } catch (error) {
    console.error("GET /api/projects/[id] error:", error);
    return NextResponse.json(
      { message: "Failed to fetch project" },
      { status: 500 }
    );
  }
}

// PUT /api/projects/:id
export async function PUT(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;

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

    // Use updateMany to avoid throwing when record doesn't exist
    const result = await prisma.project.updateMany({
      where: { id },
      data: {
        name,
        status,
        deadline: parsedDeadline,
        assignedTo,
        budget: parsedBudget,
      },
    });

    if (result.count === 0) {
      return NextResponse.json(
        { message: "Project not found" },
        { status: 404 }
      );
    }

    // Fetch updated project to return it
    const updatedProject = await prisma.project.findFirst({
      where: { id },
    });

    return NextResponse.json(updatedProject, { status: 200 });
  } catch (error) {
    console.error("PUT /api/projects/[id] error:", error);
    return NextResponse.json(
      { message: "Failed to update project" },
      { status: 500 }
    );
  }
}

// DELETE /api/projects/:id
export async function DELETE(
  _request: NextRequest,
  { params }: RouteContext
) {
  const { id } = await params;

  try {
    // Use deleteMany to avoid throwing when record doesn't exist
    const result = await prisma.project.deleteMany({
      where: { id },
    });

    if (result.count === 0) {
      return NextResponse.json(
        { message: "Project not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(
      { message: "Project deleted successfully" },
      { status: 200 }
    );
  } catch (error) {
    console.error("DELETE /api/projects/[id] error:", error);
    return NextResponse.json(
      { message: "Failed to delete project" },
      { status: 500 }
    );
  }
}
