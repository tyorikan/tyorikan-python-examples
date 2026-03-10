---
name: cloud-ops 
description: DevOps, Docker, and CI/CD patterns. Includes multi-stage Dockerfiles, docker-compose setups, GitHub Actions workflows, and Terraform basics.
---

# Cloud Operations Patterns

Standards for containerization, deployment, and infrastructure.

## Containerization

### Production-Ready Dockerfile (Python)

Uses multi-stage builds to reduce image size and improve security.
```dockerfile
# Builder stage
FROM python:3.14-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.14-slim

WORKDIR /app

# Install runtime deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

# Run as non-root user
RUN addgroup --system app && adduser --system --group app
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


## Orchestration (Dev Environment)

### docker-compose.yml
```yaml
services:
  api:
    build: 
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app_db
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app_db
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app_db"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```


## CI/CD Pipeline (GitHub Actions)

### Test & Lint Workflow
```yaml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
          
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest httpx
          
      - name: Run Tests
        run: pytest backend/tests/
        
  build-docker:
    needs: test-backend
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          
      - name: Build and Push to GCR
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT }}/my-app:${{ github.sha }} .
```


## Infrastructure as Code (Terraform)

### Basic Cloud Run Setup
```hcl
resource "google_cloud_run_service" "default" {
  name     = "my-saas-service"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/my-project/my-app:latest"
        
        env {
            name = "DATABASE_URL"
            value_from {
                secret_key_ref {
                    name = google_secret_manager_secret.db_url.secret_id
                    key  = "latest"
                }
            }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
```
