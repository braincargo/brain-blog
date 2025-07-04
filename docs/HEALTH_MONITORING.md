# Health Checks & Monitoring Guide

## 🏥 **Health Check Endpoints**

Our BrainCargo Blog Service includes comprehensive health checks designed for production Kubernetes deployments.

### **Available Endpoints**

| Endpoint | Purpose | Kubernetes Probe | Status Codes |
|----------|---------|------------------|--------------|
| `/health` | Basic health check | General monitoring | 200 |
| `/health/live` | Liveness probe | `livenessProbe` | 200, 503 |
| `/health/ready` | Readiness probe | `readinessProbe` | 200, 503 |
| `/health/startup` | Startup probe | `startupProbe` | 200, 503 |
| `/metrics` | Application metrics | Monitoring/Alerting | 200, 500 |

---

## 🎯 **Health Check Details**

### **1. Liveness Probe (`/health/live`)**
**Purpose:** Ensures the container process is running and responsive
**When to restart:** If this fails, Kubernetes will restart the pod

```json
{
  "status": "alive",
  "timestamp": "2025-06-29T18:31:26.886824+00:00",
  "service": "braincargo-blog-service",
  "uptime_seconds": 12.38
}
```

**Configuration:**
- Initial delay: 30 seconds
- Check interval: 30 seconds
- Timeout: 10 seconds
- Failure threshold: 3 attempts

### **2. Readiness Probe (`/health/ready`)**
**Purpose:** Determines if the service can handle traffic
**When ready:** When OpenAI client is available (minimum requirement)

```json
{
  "status": "ready",
  "timestamp": "2025-06-29T18:31:26.903463+00:00",
  "service": "braincargo-blog-service",
  "checks": {
    "openai_available": true,
    "assistant_api_available": false,
    "s3_available": true
  }
}
```

**Configuration:**
- Initial delay: 5 seconds
- Check interval: 10 seconds
- Timeout: 5 seconds
- Failure threshold: 3 attempts

### **3. Startup Probe (`/health/startup`)**
**Purpose:** Allows for longer startup times during initialization
**When started:** When all critical components are initialized

```json
{
  "status": "started",
  "timestamp": "2025-06-29T18:31:26.920449+00:00",
  "service": "braincargo-blog-service",
  "startup_checks": {
    "flask_app": true,
    "openai_client": true,
    "environment_loaded": true,
    "logging_configured": true
  },
  "uptime_seconds": 12.41
}
```

**Configuration:**
- Initial delay: 10 seconds
- Check interval: 10 seconds
- Timeout: 5 seconds
- Failure threshold: 10 attempts (allows up to 100 seconds startup time)

---

## 📊 **Metrics Endpoint (`/metrics`)**

Provides detailed application metrics for monitoring and alerting:

```json
{
  "service": "braincargo-blog-service",
  "version": "1.0.0",
  "timestamp": "2025-06-29T18:31:26.937000+00:00",
  "uptime_seconds": 12.43,
  "openai_status": {
    "available": true,
    "assistant_api_available": false
  },
  "s3_status": {
    "available": true
  },
  "environment": {
    "python_version": "3.12.11",
    "flask_env": "production"
  }
}
```

---

## 📝 **Logging Configuration**

### **Enhanced Application Logging**

**Format:** Structured logging with function names and line numbers
```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
```

**Example Output:**
```
2025-06-29 18:31:14,486 - __main__ - INFO - log_request_info:75 - 📥 GET /health/ready - Headers: {...} - IP: 172.17.0.1
2025-06-29 18:31:14,487 - __main__ - INFO - log_response_info:80 - 📤 GET /health/ready - Status: 200 - Size: None
```

### **Request/Response Logging**

**Before Request:** Logs all incoming requests with headers and IP
**After Request:** Logs response status codes and content length

### **Container Logging**

**Docker Compose Configuration:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service=braincargo-blog"
```

**Features:**
- JSON structured logs
- 10MB max file size
- 3 file rotation
- Service labeling for log aggregation

---

## 🚀 **Kubernetes Production Configuration**

### **Complete Deployment Example**

See `k8s-deployment.yaml` for full configuration including:

**Health Checks:**
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health/startup
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 10
```

**Resource Limits:**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

## 🔍 **Monitoring Integration**

### **Prometheus Metrics** (Future Enhancement)
The `/metrics` endpoint can be extended to provide Prometheus-compatible metrics:

```python
# Future enhancement - Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

blog_posts_generated = Counter('blog_posts_generated_total', 'Total blog posts generated')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### **Log Aggregation**
Logs are structured for easy integration with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd/Fluent Bit**
- **Grafana Loki**
- **AWS CloudWatch**
- **Google Cloud Logging**

### **Alerting Rules**
Monitor these metrics for alerting:
- Health check failures
- High error rates
- OpenAI API unavailability
- Memory/CPU usage spikes
- Response time degradation

---

## ✅ **Testing Health Checks**

### **Local Testing**
```bash
# Start container
docker run -d -p 8080:8080 -e OPENAI_API_KEY="test" braincargo-blog-service

# Test all endpoints
curl http://localhost:8080/health
curl http://localhost:8080/health/live  
curl http://localhost:8080/health/ready
curl http://localhost:8080/health/startup
curl http://localhost:8080/metrics
```

### **Kubernetes Testing**
```bash
kubectl get pods
kubectl describe pod braincargo-blog-service-xxx
kubectl logs braincargo-blog-service-xxx
```

---

## 🎯 **Best Practices**

1. **Health Check Hierarchy:**
   - Startup → Readiness → Liveness
   - Use appropriate timeouts and thresholds

2. **Logging Strategy:**
   - Structured logs for machine parsing
   - Include correlation IDs for request tracing
   - Log at appropriate levels (INFO for normal operations, ERROR for failures)

3. **Monitoring:**
   - Set up alerts on health check failures
   - Monitor application metrics trends
   - Track error rates and response times

4. **Resource Management:**
   - Set appropriate CPU/memory limits
   - Monitor resource usage patterns
   - Scale based on metrics

This comprehensive health check and monitoring setup ensures your BrainCargo Blog Service is production-ready for any container orchestration platform! 🚀 