// prisma.config.ts

import "dotenv/config";
import { defineConfig } from "@prisma/config";

// Load environment variables from .env before Prisma CLI runs
export default defineConfig({
  schema: "./prisma/schema.prisma",
});
