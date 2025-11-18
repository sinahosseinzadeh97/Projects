# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder

# Install system dependencies required for some Node/Prisma packages
RUN apk add --no-cache \
  openssl \
  libc6-compat \
  python3 \
  make \
  g++

WORKDIR /app

# Copy only package files first for better build caching
COPY package*.json ./

# Install dependencies (dev + prod, needed for build)
RUN npm install

# Copy the rest of the project files
COPY . .

# Generate Prisma client if Prisma is used
RUN npx prisma generate || echo "No prisma schema, skipping prisma generate"

# Build Next.js application
RUN npm run build

# ---------- RUNTIME STAGE ----------
FROM node:20-alpine AS runner

# Minimal system dependencies for runtime
RUN apk add --no-cache openssl libc6-compat

WORKDIR /app

ENV NODE_ENV=production

# Create non-root user for better security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy only necessary files from build stage
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/prisma ./prisma

# Next.js default port
EXPOSE 3000

# Run as non-root user
USER appuser

# Use "start" script from package.json → next start
CMD ["npm", "start"]
