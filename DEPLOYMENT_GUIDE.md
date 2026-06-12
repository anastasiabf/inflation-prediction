# Deployment Guide

## Inflation Prediction System - Deployment Instructions

### Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)

---

## Local Development

### Prerequisites
- Python 3.10+
- pip or pipenv
- Virtual environment (recommended)

### Setup

1. **Clone or navigate to project directory**
```bash
cd ./
```

2. **Create virtual environment**
```bash
make venv
```

3. **Install dependencies**
```bash
make install
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys if using production backends
```

5. **Run the pipeline**
```bash
make run-mock
```

### Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev-install   # Install with development dependencies
make run           # Run full pipeline
make run-mock      # Run with mock LLM backend
make test          # Run tests
make lint          # Check code quality
make format        # Format code automatically
make clean         # Remove build artifacts
```

---

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Build and Run

```bash
# Build image
docker build -f deployment/Dockerfile -t inflation-prediction:latest .

# Run container
docker run -v $(pwd)/inflation_prediction_output:/app/inflation_prediction_output \
           -e LLM_BACKEND=mock \
           inflation-prediction:latest

# Or use docker-compose
docker-compose up
```

### Production Build

```bash
docker build --build-arg ENVIRONMENT=production \
             -f deployment/Dockerfile \
             -t inflation-prediction:prod .
```

---

## Cloud Deployment

### AWS ECS

```bash
# Tag image for ECR
docker tag inflation-prediction:latest \
  <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/inflation-prediction:latest

# Push to ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/inflation-prediction:latest

# Deploy to ECS
aws ecs create-service --cluster inflation-cluster \
  --service-name inflation-prediction \
  --task-definition inflation-prediction:1 \
  --desired-count 1
```

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/<PROJECT_ID>/inflation-prediction
gcloud run deploy inflation-prediction \
  --image gcr.io/<PROJECT_ID>/inflation-prediction \
  --platform managed \
  --region us-central1 \
  --memory 2Gi
```

---

## Environment Configuration

### Development (.env)

```
LLM_BACKEND=mock
OPENAI_API_KEY=<your_key>
ANTHROPIC_API_KEY=<your_key>
DATA_OUTPUT_DIR=inflation_prediction_output
MONTHS=36
LOG_LEVEL=INFO
```

### Production (.env.production)

```
LLM_BACKEND=openai
OPENAI_API_KEY=<your_production_key>
DATA_OUTPUT_DIR=/data/output
MONTHS=36
LOG_LEVEL=WARNING
USE_CACHE=true
```

---

## Serving the Dashboard

### Local HTTP Server

```bash
# Using Python
cd public/
python -m http.server 8000

# Or using nginx (via docker-compose)
docker-compose up web-server
```

Access at: `http://localhost:8000/index.html`

---

## Monitoring & Logging

### View Execution Logs

```bash
tail -f inflation_prediction_output/execution_log.json
```

### Health Check

```bash
# Check if pipeline completed successfully
if [ -f inflation_prediction_output/index.html ]; then
    echo "✓ Dashboard generated successfully"
else
    echo "✗ Pipeline failed"
fi
```

---

## Troubleshooting

### Issue: "Module not found"
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
```

### Issue: "API key not found"
```bash
# Check .env file exists and has correct keys
cat .env
```

### Issue: "Port already in use"
```bash
# Use different port
python -m http.server 8001
```

---

## Performance Optimization

### Caching Results

```python
from src.inflation_prediction.main_orchestrator import InflationPredictionOrchestrator

orchestrator = InflationPredictionOrchestrator()
# Results cached in inflation_prediction_output/
```

### Parallel Processing (Future)

Currently single-threaded (~30 seconds). Future version will support:
- Parallel data ingestion
- Parallel LLM calls
- Batch processing

---

## Support & Resources

- **Documentation**: See README.md
- **Quick Start**: See QUICK_START.md
- **System Details**: See SYSTEM_DOCUMENTATION.md
- **Architecture**: See TECHNICAL_ARCHITECTURE.md

