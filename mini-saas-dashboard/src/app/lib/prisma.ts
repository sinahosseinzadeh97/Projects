// src/app/lib/prisma.ts

import { PrismaClient } from "@prisma/client";

// Use a global variable to avoid creating multiple PrismaClient instances in development.
// This prevents "PrismaClient is already running" errors during hot-reload.
const globalForPrisma = globalThis as unknown as {
  prisma?: PrismaClient;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: ["query", "error", "warn"],
  });

// Store the PrismaClient instance on the global object in development
if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
