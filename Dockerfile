# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependencies first (for build caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Expose the FastAPI port
EXPOSE 8000

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ || exit 1

# Start FastAPI (points to app/main.py)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
