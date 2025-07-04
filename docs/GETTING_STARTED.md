# Getting Started with BrainCargo Blog Service

> **Complete setup guide for local development and Docker deployment**

## 🚀 Quick Start

The fastest way to get the BrainCargo Blog Service running:

```bash
# 1. Clone and navigate to the project
cd brain-blog

# 2. Set up your OpenAI API key (required)
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# 3. Start the service with Docker
make docker-up

# 4. Test the service
curl http://localhost:8080/health
```

The service will be available at `http://localhost:8080`

## 📋 Prerequisites

### Required
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **OpenAI API Key** with Responses API access

### Optional (for enhanced features)
- **Anthropic API Key** for Claude models
- **Grok API Key** for xAI integration  
- **Gemini API Key** for Google AI
- **AWS credentials** for S3 blog storage

## ⚙️ Environment Setup

### Method 1: Environment Variables (Recommended)

```bash
# Required
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Optional providers
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GROK_API_KEY="xai-your-grok-key-here"
export GEMINI_API_KEY="your-gemini-key-here"

# Optional S3 storage
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export BLOG_POSTS_BUCKET="your-bucket-name"
```

### Method 2: Configuration File

Create `config/.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional providers
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GROK_API_KEY=xai-your-grok-key-here
GEMINI_API_KEY=your-gemini-key-here

# Optional S3 storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
BLOG_POSTS_BUCKET=your-bucket-name
AUTHORIZED_PHONE_NUMBER=your-phone-number
```

Then load it:
```bash
set -a; source config/.env; set +a
```

## 🐳 Docker Commands

### Basic Operations

```bash
# Start the service
make docker-up

# View logs
make docker-logs

# Restart service
make docker-restart

# Stop service
make docker-down

# Clean up resources
make docker-clean
```

### Development Workflow

```bash
# 1. Start development environment
make docker-up

# 2. Make code changes (auto-reloaded due to volume mount)

# 3. View logs to debug
make docker-logs

# 4. Restart if needed
make docker-restart

# 5. Stop when done
make docker-down
```

### Advanced Commands

```bash
# Force rebuild from scratch
make docker-rebuild

# Check service status
make docker-status

# View service configuration
docker-compose config
```

## 🧪 Testing Your Setup

### Quick Health Check

```bash
# Test basic connectivity
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "openai_available": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Test Blog Generation

```bash
# Test with a sample URL
curl -X POST "http://localhost:8080/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=%2B115551231234&Body=Generate blog about https://example.com/ai-article"
```

### Run Test Suite

```bash
# Quick pipeline tests
make test-quick

# Complete test suite
make test

# Test specific components
make test-unit
```

## 🔧 Troubleshooting

### Common Issues

#### Service won't start
```bash
# Check if port 8080 is in use
lsof -i :8080

# View detailed logs
make docker-logs

# Try clean restart
make docker-clean && make docker-up
```

#### Environment variables not loading
```bash
# Verify .env file exists
ls -la config/.env

# Check environment setup
make env-check

# Test configuration loading
python -c "import os; print('OPENAI_API_KEY' in os.environ)"
```

#### Permission issues
```bash
# Reset Docker environment
make docker-clean
docker system prune -a
make docker-rebuild
```

#### API key errors
```bash
# Verify API key format
echo $OPENAI_API_KEY | cut -c1-10  # Should show "sk-proj-" or "sk-"

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | head -20
```

### Debug Mode

Enable detailed logging:

```bash
# Set debug environment
export DEBUG=true

# Start with verbose logging
make docker-up

# Monitor logs in real-time
make docker-logs -f
```

## 🌐 Service Endpoints

Once running, the service provides:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/health/ready` | GET | Readiness probe |
| `/health/live` | GET | Liveness probe |
| `/webhook` | POST | SMS webhook (Twilio) |
| `/generate` | POST | Direct blog generation |
| `/providers/status` | GET | Provider status |

### Example Usage

```bash
# Check all providers
curl http://localhost:8080/providers/status

# Generate blog from URL
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## ⚡ Performance Tips

### Resource Optimization

```bash
# Limit memory usage
docker-compose up --compatibility

# Use specific CPU limits
docker run --cpus=".5" --memory="512m" braincargo-blog-service
```

### Caching

The service includes built-in caching for:
- Configuration loading
- Provider initialization  
- Template rendering

## 🔐 Security Considerations

### API Key Security

```bash
# Never commit API keys to version control
echo "config/.env" >> .gitignore

# Use environment variables in production
export OPENAI_API_KEY="$(cat /path/to/secret)"
```

### Network Security

```bash
# Run on localhost only (default)
docker-compose up  # Binds to 127.0.0.1:8080

# Expose to network (production)
# Edit docker-compose.yml ports: "0.0.0.0:8080:8080"
```

## 📦 Production Deployment

For production deployment, see:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production guide
- **[HEALTH_MONITORING.md](HEALTH_MONITORING.md)** - Monitoring setup

### Quick Production Checklist

- [ ] Set all required environment variables
- [ ] Configure health checks
- [ ] Set up logging and monitoring
- [ ] Configure reverse proxy (nginx/CloudFlare)
- [ ] Set up SSL/TLS certificates
- [ ] Configure backups for S3 storage

## 🧠 Vector Store Setup (Optional)

For enhanced AI capabilities with knowledge files:

### Setup Knowledge Base

```bash
# 1. Create vector_store_docs directory with your knowledge files
mkdir vector_store_docs
# Add .md, .txt, or .pdf files to vector_store_docs/

# 2. Install vector store dependencies
make vector-install

# 3. Upload to OpenAI vector store
make vector-upload-openai

# 4. Upload to Anthropic (optional)
make vector-upload-anthropic

# 5. Check status
make vector-status
```

### Supported File Types

- **Markdown files** (`.md`) - Documentation, guides
- **Text files** (`.txt`) - Plain text knowledge
- **PDF files** (`.pdf`) - Documents, manuals
- **JSON files** (`.json`) - Structured data

### Vector Store Benefits

- **Enhanced Context**: AI has access to your specific knowledge base
- **Better Accuracy**: Responses informed by your documentation
- **Consistent Branding**: Maintains your company voice and terminology
- **Domain Expertise**: AI can reference technical specifications

## 💡 Next Steps

1. **Test the basic setup** with `make test-quick`
2. **Configure additional providers** (Anthropic, Grok, Gemini)
3. **Set up vector stores** with your knowledge files
4. **Set up S3 storage** for blog persistence
5. **Customize prompts** in `prompts/` directory
6. **Integrate with Twilio** for SMS functionality

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: `make docker-logs`
2. **Verify environment**: `make env-check`
3. **Run diagnostics**: `make test-quick`
4. **Clean restart**: `make docker-clean && make docker-up`

For more detailed information, see the complete documentation in the `docs/` directory. 