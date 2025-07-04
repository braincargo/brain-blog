# BrainCargo Blog Service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

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
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Set proper permissions
RUN chown -R appuser:appuser /app && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true

# Create volume mount points
VOLUME ["/app/config", "/app/prompts", "/app/vector_store_docs", "/app/openai_store", "/app/local_output"]

# Expose port
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start the application
CMD ["python", "app.py"] 