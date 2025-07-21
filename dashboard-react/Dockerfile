# ================================
# Multi-stage Docker build for React Dashboard
# Using Node.js 18 Alpine for smaller image size
# ================================

# Build stage
FROM node:18-alpine AS builder

# Accept build arguments for API configuration
ARG API_BASE_URL=http://localhost:8000
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Set environment variables for build
ENV API_BASE_URL=${API_BASE_URL}
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Set working directory
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json ./

# Install dependencies with npm cache mount for faster builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# ================================
# Production stage
# ================================
FROM node:18-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S nodegroup \
    && adduser -S nodeuser -u 1001 -G nodegroup

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Set working directory
WORKDIR /app

# Copy standalone output from build stage
COPY --from=builder --chown=nodeuser:nodegroup /app/.next/standalone ./
COPY --from=builder --chown=nodeuser:nodegroup /app/.next/static ./.next/static
COPY --from=builder --chown=nodeuser:nodegroup /app/public ./public

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Switch to non-root user
USER nodeuser

# Expose port
EXPOSE 3000

# Start the application with proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
