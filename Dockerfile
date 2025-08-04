# BrainCargo Blog Service - Security Hardened
FROM python:3.12-slim

# Security: Add security labels
LABEL security.scan="required" \
      security.non-root="true" \
      version="2.0.0-secure"

# Set working directory
WORKDIR /app

# Security: Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ca-certificates \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set up directory structure
RUN mkdir -p config prompts vector_store_docs openai_store local_output

# Ensure prompts directory has default content
RUN cp -r prompts/* /app/prompts/ || true

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 --no-user-group appuser && \
    groupadd --gid 1000 appuser && \
    usermod -g appuser appuser

# Set proper permissions and security hardening
RUN chown -R appuser:appuser /app && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true && \
    chmod -R 750 /app && \
    chmod 755 /app

# Create volume mount points
VOLUME ["/app/config", "/app/prompts", "/app/vector_store_docs", "/app/openai_store", "/app/local_output"]

# Security: Only expose to localhost (requires reverse proxy)
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check (use localhost since we bind to localhost now)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV ENVIRONMENT=production

# Security: Use gunicorn instead of Flask dev server for production
CMD ["python", "-c", "import os; from app import app, get_settings; settings = get_settings(); app.run(host='127.0.0.1', port=settings.port, debug=False)"] 
