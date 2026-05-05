# ============================================================
# SOCsentinel — Multi-stage Dockerfile for Hugging Face Spaces
# ============================================================
# Builds React frontend → serves via FastAPI StaticFiles
# Compatible with HF Spaces Docker SDK
# ============================================================

# --- Stage 1: Build Frontend ---
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --production=false
COPY frontend/ ./
RUN npx vite build

# --- Stage 2: Python Backend ---
FROM python:3.11-slim AS production

# HF Spaces metadata
LABEL maintainer="SOCsentinel Team"
LABEL org.opencontainers.image.title="SOCsentinel"
LABEL org.opencontainers.image.description="Multi-Agent LLM Assistant for SOC Analysts"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (HF Spaces requirement)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/app ./app
COPY backend/prompts ./prompts
COPY backend/.env.example ./.env

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./static

# Create data directories
RUN mkdir -p data/chroma_db && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (HF Spaces uses 7860 by default)
EXPOSE 7860

# Environment
ENV PORT=7860
ENV ENVIRONMENT=production
ENV LLM_PROVIDER=mock
ENV CHROMA_PERSIST_DIR=./data/chroma_db
ENV LOG_LEVEL=INFO
ENV FRONTEND_URL=*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
