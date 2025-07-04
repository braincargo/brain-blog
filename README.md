# BrainCargo Blog Service

> **Multi-Provider AI-Powered Blog Generation Service** with flexible content pipeline

## 🚀 Overview

The BrainCargo Blog Service is a sophisticated, containerized microservice that automatically generates professional blog posts from URLs, topics, or custom content. The system supports multiple AI providers (OpenAI, Anthropic, Gemini, Grok) and includes intelligent content extraction, categorization, and media generation capabilities.

### 🎯 Key Features

- **Multi-Provider AI Support**: OpenAI, Anthropic Claude, Google Gemini, and Grok
- **Flexible Input Sources**: URLs, topics, or custom content
- **Smart Content Extraction**: Automatic web scraping and content processing
- **AI-Powered Categorization**: Intelligent content classification
- **Image Generation**: BrainCargo featured images and memes
- **Configurable Branding**: Customizable company name, domain, and styling
- **Docker Deployment**: Containerized for reliable cross-platform deployment
- **Comprehensive Testing**: Full test suite with multiple provider support
- **Professional Documentation**: Complete setup and usage guides

## 🏗️ Architecture

```
Input (URL/Topic/Content) → Content Processor → AI Provider → Blog Generator → Output Storage
                                    ↓
                          Content Categorization → Image Generation → Media Storage
```

### Components

1. **Flask Web Service**: RESTful API for blog generation
2. **Multi-Provider AI**: Support for OpenAI, Anthropic, Gemini, and Grok
3. **Content Pipeline**: Extraction, categorization, and processing
4. **Image Generation**: AI-powered visual content creation
5. **Media Storage**: Configurable storage backends
6. **Configuration Management**: Centralized, type-safe configuration

## 📋 Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional)
- At least one AI provider API key:
  - OpenAI API key
  - Anthropic API key
  - Google AI API key
  - Grok API key

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd brain-blog/blog-service
```

### 2. Environment Configuration

Create a `.env` file based on the example:

```bash
cp config/environment.example .env
```

Edit the `.env` file with your configuration:

```bash
# AI Provider Configuration (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Blog Configuration
BLOG_DOMAIN=braincargo.com
COMPANY_NAME=BrainCargo LLC
CDN_URL=https://cdn.braincargo.com
CALL_TO_ACTION=Visit our website

# Security (optional)
AUTHORIZED_PHONE=1234567890

# Debug mode
DEBUG=false
PORT=8080

# Optional for vector store integration
OPENAI_VECTOR_STORE_IDS=vs_store_id1,vs_store_id2
ANTHROPIC_FILE_IDS=file_id1,file_id2,file_id3
```

### 3. Installation

#### Option A: Docker (Recommended)

```bash
# Build and start the service
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

#### Option B: Direct Python Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Run the application
python app.py
```

### 4. Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000+00:00",
  "providers_available": {
    "openai": true,
    "anthropic": true,
    "gemini": false,
    "grok": false
  }
}
```

### 5. Setup Knowledge Base (Optional)

Enhance AI capabilities with your company's knowledge:

```bash
# Install vector store dependencies
make vector-install

# Upload documentation to vector stores
make vector-upload-all

# Check status
make vector-status
```

## 🔧 Configuration

### AI Provider Configuration

The service supports multiple AI providers. Configure at least one:

```python
# Provider priority (first available is used)
PROVIDER_PRIORITY = ["anthropic", "openai", "gemini", "grok"]
```

### Blog Configuration

Customize the blog generation settings:

```bash
# Blog Settings
BLOG_DOMAIN=braincargo.com           # Your blog domain
COMPANY_NAME=BrainCargo LLC Name       # Company branding
CDN_URL=https://cdn.braincargo.com   # CDN for media assets
CALL_TO_ACTION=Visit our website     # Custom call-to-action

# Content Settings
DEFAULT_CATEGORY=Technology          # Default blog category
MAX_CONTENT_LENGTH=5000             # Maximum content length
ENABLE_IMAGE_GENERATION=true        # Generate featured images
ENABLE_MEME_GENERATION=true         # Generate meme content
```

## 📝 Usage Examples

### Generate Blog from URL

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "provider": "openai"
  }'
```

### Generate Blog from Topic

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Future of Artificial Intelligence",
    "provider": "anthropic",
    "style": "tech"
  }'
```

### Generate Blog from Custom Content

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Custom content to transform into a blog post",
    "title": "Custom Blog Post",
    "provider": "gemini"
  }'
```

### Response Format

```json
{
  "success": true,
  "blog": {
    "title": "Generated Blog Title",
    "content": "Full blog content in HTML format...",
    "summary": "Brief summary of the blog post",
    "category": "Technology",
    "featured_image": "https://cdn.braincargo.com/images/featured.jpg",
    "timestamp": "2025-01-01T12:00:00.000000+00:00"
  },
  "metadata": {
    "provider": "openai",
    "generation_time": 8.5,
    "content_source": "url"
  }
}
```

## 🚀 Advanced Features

### Content Categorization

The service automatically categorizes content using AI:

```python
# Supported categories
CATEGORIES = [
    "Technology", "Business", "Science", "Health",
    "Education", "Entertainment", "Sports", "Politics",
    "Finance", "Travel", "Food", "Lifestyle"
]
```

### Image Generation

Generate featured images and memes:

```bash
# Enable in configuration
ENABLE_IMAGE_GENERATION=true
ENABLE_MEME_GENERATION=true

# Images are automatically generated and stored
```

### Multi-Style Support

Choose from different writing styles:

- `tech`: Technical and professional
- `web3`: Blockchain and cryptocurrency focus  
- `security`: Cybersecurity emphasis
- `general`: Balanced, accessible tone

## 🧪 Testing

### Run All Tests

```bash
# Run the complete test suite
python test_all.py

# Run specific test modules
python test_blog_generation.py
python test_complete_pipeline.py
python test_image_fallbacks.py
```

### Test Individual Providers

```bash
# Test OpenAI provider
python -m pytest providers/test_openai.py

# Test Anthropic provider  
python -m pytest providers/test_anthropic.py
```

### Local Testing

```bash
# Test with local configuration
python test_local.py
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build production image
docker build -t brain-blog:latest .

# Run with production settings
docker run -d \
  --name brain-blog \
  -p 8080:8080 \
  --env-file .env \
  brain-blog:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  blog-generator:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - BLOG_DOMAIN=${BLOG_DOMAIN}
    volumes:
      - ./generated_blogs:/app/generated_blogs
      - ./local_output:/app/local_output
```

## 📊 Performance & Monitoring

### Performance Metrics

- **Response Times**: 5-15 seconds typical generation time
- **Throughput**: Handles concurrent requests efficiently
- **Resource Usage**: ~200MB memory, minimal CPU when idle
- **Success Rate**: 95%+ with multi-provider fallback

### Monitoring Endpoints

```bash
# Health check
GET /health

# Metrics (if enabled)
GET /metrics

# Provider status
GET /providers/status
```

## 🔐 Security

### Best Practices

1. **API Key Protection**: Store keys in environment variables
2. **Input Validation**: All inputs are sanitized and validated
3. **Rate Limiting**: Configure appropriate limits for your use case
4. **Phone Authorization**: Optional phone number authorization
5. **Network Security**: Use HTTPS in production
6. **Container Security**: Run with non-root user

### Authorization

Optional phone-based authorization:

```bash
# Configure authorized phone numbers
AUTHORIZED_PHONE=1234567890

# Or disable authorization
AUTHORIZED_PHONE=""
```

## 📚 API Documentation

### Core Endpoints

- `POST /generate` - Generate blog post
- `GET /health` - Service health check
- `GET /providers/status` - AI provider status
- `POST /webhook` - Webhook endpoint (if enabled)

### Request/Response Schemas

See the [documentation directory](docs/) for detailed API documentation and schemas.

## 📚 Documentation

For comprehensive documentation including setup guides, architecture details, deployment strategies, and more, see the **[docs/](docs/)** directory:

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete setup and configuration
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and technical details
- **[Testing Guide](docs/TESTING.md)** - Comprehensive testing documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment strategies
- **[Health Monitoring](docs/HEALTH_MONITORING.md)** - Monitoring and observability

For a complete documentation index, see **[docs/README.md](docs/README.md)**.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
black .
isort .
flake8 .

# Run type checking
mypy .

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Troubleshooting

1. **Check logs**: `docker logs brain-blog`
2. **Verify configuration**: Ensure API keys are valid
3. **Test providers**: Use `/providers/status` endpoint
4. **Check resources**: Ensure sufficient memory/CPU

### Common Issues

- **API Key Errors**: Verify keys are correct and have sufficient quota
- **Content Extraction Failures**: Some sites block automated access
- **Generation Timeouts**: Increase timeout values for complex content
- **Provider Unavailable**: Service will fallback to next available provider

### Getting Help

- Check the `/docs` directory for detailed documentation
- Review test files for usage examples
- Open an issue on GitHub for bugs or feature requests

---

**🎉 Start generating AI-powered blog content with multiple provider support and professional-grade features!** 