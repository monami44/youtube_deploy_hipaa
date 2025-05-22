FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects anonymous telemetry data about general usage
ENV NEXT_TELEMETRY_DISABLED=1

# Accept build arguments
ARG NEXT_PUBLIC_API_URL
ARG AZURE_STORAGE_ACCOUNT_NAME
ARG AZURE_STORAGE_ACCOUNT_KEY
ARG AZURE_STORAGE_CONTAINER_NAME

# Set environment variables from build arguments
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV AZURE_STORAGE_ACCOUNT_NAME=${AZURE_STORAGE_ACCOUNT_NAME}
ENV AZURE_STORAGE_ACCOUNT_KEY=${AZURE_STORAGE_ACCOUNT_KEY}
ENV AZURE_STORAGE_CONTAINER_NAME=${AZURE_STORAGE_CONTAINER_NAME}

# Build the Next.js application
RUN npm run build --legacy-peer-deps

# Production image, copy all files
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Pass build args to the runner stage
ARG NEXT_PUBLIC_API_URL
ARG AZURE_STORAGE_ACCOUNT_NAME
ARG AZURE_STORAGE_ACCOUNT_KEY
ARG AZURE_STORAGE_CONTAINER_NAME

# Set environment variables in the runner stage
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV AZURE_STORAGE_ACCOUNT_NAME=${AZURE_STORAGE_ACCOUNT_NAME}
ENV AZURE_STORAGE_ACCOUNT_KEY=${AZURE_STORAGE_ACCOUNT_KEY}
ENV AZURE_STORAGE_CONTAINER_NAME=${AZURE_STORAGE_CONTAINER_NAME}

# Copy startup script first and make it executable
COPY startup.sh ./
RUN chmod +x ./startup.sh

# Copy all files from the builder stage
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.ts ./

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Start with our shell script that loads env vars
CMD ["./startup.sh"] 