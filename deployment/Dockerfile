FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/
COPY public/ ./public/
COPY tests/ ./tests/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p /app/inflation_prediction_output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run the pipeline
CMD ["python", "-m", "src.inflation_prediction.main_orchestrator"]
