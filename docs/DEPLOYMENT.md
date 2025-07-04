# Deployment Guide

> **Production-ready deployment strategies for the BrainCargo Blog Service**

## 🚀 Deployment Overview

This guide covers multiple deployment strategies for the BrainCargo Blog Service, from local development to production cloud environments.

## 🔧 Prerequisites

### Required Tools

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **OpenAI API Key** with Responses API access
- **AWS Account** with S3 access (for blog storage)
- **Twilio Account** (for SMS webhooks) - optional for testing

### Required Credentials

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# AWS (for S3 storage)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-west-2

# BrainCargo Config
S3_BUCKET_NAME=your-bucket-name
AUTHORIZED_PHONE=15551231234
```

## 🏠 Local Development

### Quick Start

```bash
# 1. Navigate to service directory
cd blog-service

# 2. Create environment file
cp config/.env.example config/.env
# Edit config/.env with your credentials

# 3. Build and run
make docker-up

# 4. Test health endpoint
curl http://localhost:8080/health
```

### Development Environment

```yaml
# docker-compose.yml (development)
version: '3.8'
services:
  braincargo-blog-service:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEBUG=true
      - PORT=8080
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs  # Mount logs for debugging
    restart: unless-stopped
```

### Development Testing

```bash
# Test with sample URL
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+115551231234&Body=Generate blog about https://amgreatness.com/2025/06/14/can-ai-improve-election-integrity/"

# Monitor logs in real-time
docker logs -f docker-blog-service-braincargo-blog-service-1

# Run health checks
curl http://localhost:8080/health | jq
```

## 🌐 Production Deployment

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  braincargo-blog-service:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEBUG=false
      - PORT=8080
    env_file:
      - .env.prod
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
```

### Production Deployment Commands

```bash
# Build for production
docker-compose -f docker-compose.prod.yml build --no-cache

# Deploy in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl https://braincargo.com/health

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Environment File

```bash
# .env.prod
OPENAI_API_KEY=your_production_api_key
AWS_ACCESS_KEY_ID=your_production_aws_key
AWS_SECRET_ACCESS_KEY=your_production_aws_secret
AWS_DEFAULT_REGION=us-west-2
S3_BUCKET_NAME=braincargo-blog-production
BLOG_POSTS_PREFIX=blog
AUTHORIZED_PHONE=15551231234
DEBUG=false
PORT=8080
```

## ☁️ Cloud Deployment Options

### 1. AWS ECS/Fargate

#### Task Definition

```json
{
  "family": "braincargo-blog-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "braincargo-blog-service",
      "image": "your-ecr-repo/braincargo-blog-service:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PORT", "value": "8080"},
        {"name": "DEBUG", "value": "false"}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-api-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/braincargo-blog-service",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### ECS Deployment Commands

```bash
# Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-west-2.amazonaws.com

docker build -t braincargo-blog-service .
docker tag braincargo-blog-service:latest your-account.dkr.ecr.us-west-2.amazonaws.com/braincargo-blog-service:latest
docker push your-account.dkr.ecr.us-west-2.amazonaws.com/braincargo-blog-service:latest

# Create ECS service
aws ecs create-service \
  --cluster braincargo-cluster \
  --service-name braincargo-blog-service \
  --task-definition braincargo-blog-service:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### 2. Google Cloud Run

#### Dockerfile Optimization for Cloud Run

```dockerfile
# Multi-stage build for Cloud Run
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

# Copy dependencies from builder stage
COPY --from=builder /root/.local /root/.local

WORKDIR /app
COPY . .

# Cloud Run expects PORT environment variable
ENV PORT=8080
ENV PYTHONPATH=/root/.local/lib/python3.12/site-packages

# Use gunicorn for production
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

#### Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/your-project/braincargo-blog-service

gcloud run deploy braincargo-blog-service \
  --image gcr.io/your-project/braincargo-blog-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=false \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest \
  --memory 1Gi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 10
```

### 3. Azure Container Instances

#### Azure Deployment

```bash
# Create resource group
az group create --name braincargo-rg --location eastus

# Deploy container
az container create \
  --resource-group braincargo-rg \
  --name braincargo-blog-service \
  --image your-registry/braincargo-blog-service:latest \
  --dns-name-label braincargo-blog \
  --ports 8080 \
  --environment-variables DEBUG=false PORT=8080 \
  --secure-environment-variables OPENAI_API_KEY=your-api-key \
  --cpu 1 \
  --memory 1 \
  --restart-policy Always
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy BrainCargo Blog Service

on:
  push:
    branches: [main]
    paths: ['blog-service/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and test
        run: |
          cd blog-service
          make docker-build
          make test-quick

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push to ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: braincargo-blog-service
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd blog-service
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster braincargo-cluster \
            --service braincargo-blog-service \
            --force-new-deployment
```

## 🔍 Monitoring & Observability

### Health Check Configuration

```python
# Enhanced health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': os.environ.get('APP_VERSION', 'development'),
        'openai_available': OPENAI_AVAILABLE,
        'assistant_api_available': ASSISTANT_API_AVAILABLE,
        's3_available': s3_client is not None,
        'uptime_seconds': time.time() - start_time,
        'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024
    }
    
    # Test OpenAI connectivity
    if OPENAI_AVAILABLE:
        try:
            openai_client.models.list()
            status['openai_connectivity'] = 'ok'
        except Exception as e:
            status['openai_connectivity'] = 'error'
            status['openai_error'] = str(e)
    
    # Test S3 connectivity
    if s3_client:
        try:
            s3_client.list_buckets()
            status['s3_connectivity'] = 'ok'
        except Exception as e:
            status['s3_connectivity'] = 'error'
            status['s3_error'] = str(e)
    
    return jsonify(status), 200
```

### Logging Configuration

```python
# Production logging setup
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/braincargo-blog.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('BrainCargo Blog Service startup')
```

### Metrics Collection

```python
# Prometheus metrics (optional)
from prometheus_client import Counter, Histogram, generate_latest

blog_posts_generated = Counter('blog_posts_generated_total', 'Total blog posts generated')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## 🔐 Security Configuration

### Production Security Headers

```python
from flask_talisman import Talisman

# Security headers for production
if not app.debug:
    Talisman(app, {
        'force_https': True,
        'strict_transport_security': True,
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': "'self'",
            'style-src': "'self' 'unsafe-inline'",
        }
    })
```

### Environment Variable Security

```bash
# Use secrets management in production
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name "braincargo-blog-service/openai" \
  --description "OpenAI API key for blog service" \
  --secret-string "your-openai-api-key"

# Kubernetes secrets
kubectl create secret generic braincargo-secrets \
  --from-literal=openai-api-key=your-openai-api-key \
  --from-literal=aws-access-key-id=your-aws-key
```

## 📊 Performance Optimization

### Production Optimizations

```dockerfile
# Optimized production Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
```

### Resource Limits

```yaml
# Kubernetes deployment with resource limits
apiVersion: apps/v1
kind: Deployment
metadata:
  name: braincargo-blog-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: braincargo-blog-service
  template:
    metadata:
      labels:
        app: braincargo-blog-service
    spec:
      containers:
      - name: braincargo-blog-service
        image: your-registry/braincargo-blog-service:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: DEBUG
          value: "false"
        - name: PORT
          value: "8080"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🚨 Disaster Recovery

### Backup Strategy

```bash
# Automated S3 backup script
#!/bin/bash
# backup-s3.sh

BUCKET="braincargo-blog-production"
BACKUP_BUCKET="braincargo-blog-backup"
DATE=$(date +%Y%m%d-%H%M%S)

# Sync blog posts to backup bucket
aws s3 sync s3://$BUCKET/blog/ s3://$BACKUP_BUCKET/blog-backup-$DATE/ \
  --exclude "*" --include "*.json"

echo "Backup completed: blog-backup-$DATE"
```

### Rollback Strategy

```bash
# Quick rollback script
#!/bin/bash
# rollback.sh

PREVIOUS_IMAGE_TAG=$1

if [ -z "$PREVIOUS_IMAGE_TAG" ]; then
  echo "Usage: ./rollback.sh <previous-image-tag>"
  exit 1
fi

# Update ECS service to previous image
aws ecs update-service \
  --cluster braincargo-cluster \
  --service braincargo-blog-service \
  --task-definition braincargo-blog-service:$PREVIOUS_IMAGE_TAG \
  --force-new-deployment

echo "Rollback initiated to image tag: $PREVIOUS_IMAGE_TAG"
```

## 📈 Scaling Considerations

### Horizontal Scaling

- **Load Balancer**: Use ALB/ELB for multiple instances
- **Auto Scaling**: Configure based on CPU/memory metrics
- **Database**: Consider external database for high-volume deployments
- **Caching**: Implement Redis for frequently accessed data

### Vertical Scaling

- **Memory**: 512MB minimum, 1GB recommended for production
- **CPU**: 1 core minimum, 2 cores for high-traffic
- **Storage**: Minimal (logs only), S3 for persistent data

## ✅ Deployment Checklist

### Pre-Deployment

- [ ] **Environment variables configured**
- [ ] **OpenAI API key valid and funded**
- [ ] **AWS credentials have S3 access**
- [ ] **S3 bucket exists and accessible**
- [ ] **Docker image built and tested**
- [ ] **Health checks passing locally**

### Deployment

- [ ] **Deploy to staging environment first**
- [ ] **Run integration tests**
- [ ] **Verify health endpoint**
- [ ] **Test webhook functionality**
- [ ] **Monitor logs for errors**

### Post-Deployment

- [ ] **Verify service is running**
- [ ] **Test blog generation end-to-end**
- [ ] **Check S3 storage is working**
- [ ] **Monitor performance metrics**
- [ ] **Set up alerts and monitoring**

---

**🎉 Your BrainCargo Auto Blog Publisher is now ready for production deployment!** 🚀 