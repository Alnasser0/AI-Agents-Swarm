# ================================
# Multi-stage Docker build for AI Agents Swarm
# Using Python 3.11 Alpine for smaller image size
# ================================

# Build stage
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ================================
# Production stage
# ================================
FROM python:3.11-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup \
    && adduser -S appuser -u 1001 -G appgroup

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code with correct ownership
COPY --chown=appuser:appgroup . .

# Create necessary directories with correct permissions
RUN mkdir -p data logs \
    && chown -R appuser:appgroup data logs

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
