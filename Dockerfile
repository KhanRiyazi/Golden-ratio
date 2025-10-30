# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only dependencies first (for build caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ADMIN_KEY=${ADMIN_KEY:-changeme}

# Expose the app port (Railway will map it automatically)
EXPOSE 8000

# Create a non-root user for security
RUN useradd -m appuser
USER appuser

# Healthcheck (optional)
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ || exit 1

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
