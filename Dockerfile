FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Create non-root user (required by Hugging Face Spaces)
RUN useradd -m -u 1000 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create writable directories for local data fallback
RUN mkdir -p /app/local_data && chown -R appuser:appuser /app

USER appuser

# Hugging Face Spaces uses port 7860; configurable via PORT env var
ENV PORT=7860
EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
