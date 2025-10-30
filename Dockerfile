# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only dependencies first (for build caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Expose the app port
EXPOSE 8000

# Create a non-root user and give ownership
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Healthcheck (uses installed curl)
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ || exit 1

# Dynamically pick up Railway's assigned port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
