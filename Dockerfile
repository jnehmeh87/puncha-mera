# Builder stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc pkg-config libcairo2-dev libgirepository1.0-dev python3-dev python3-pip libffi-dev libpango-1.0-0 libpangoft2-1.0-0 libglib2.0-dev

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser

WORKDIR /home/appuser/app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Copy run script
COPY run.sh .

# Set ownership
RUN chown -R appuser:appuser /home/appuser/app

# Set the user
USER appuser

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Run the application
CMD ["./run.sh"]
