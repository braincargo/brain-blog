# BrainCargo Blog Service

> **AI-powered blog generation service with multi-provider support and intelligent content processing**

## 🚀 Overview

The BrainCargo Blog Service is a production-ready microservice that automatically generates professional blog posts from URLs using state-of-the-art AI models. Built with modern cloud-native architecture, it supports multiple AI providers, intelligent content categorization, and comprehensive media generation.

### Key Features

- **🤖 Multi-Provider AI Support** - OpenAI, Anthropic, Grok, and Gemini integration
- **📝 Intelligent Categorization** - Automatic content classification and style adaptation  
- **🎨 Media Generation** - Automated image and meme creation with S3 storage
- **🧠 Knowledge Base Integration** - Vector stores and file uploads for enhanced context
- **🔄 Robust Fallback System** - Automatic provider switching for maximum reliability
- **🐳 Container-Ready** - Docker deployment with Kubernetes support
- **📊 Production Monitoring** - Comprehensive health checks and observability

## 🏗️ Architecture

### Modern Microservice Design

```
SMS/API Input → Content Extraction → AI Categorization → 
Blog Generation → Media Creation → Storage → Final Output
```

The service is built on a modular pipeline architecture with:

- **Provider Abstraction Layer** - Unified interface for multiple AI services
- **Configuration-Driven** - YAML-based configuration for easy customization
- **Containerized Deployment** - Docker and Kubernetes ready
- **Comprehensive Testing** - 90%+ test coverage with automated CI/CD

### Multi-Provider Support

| Provider | Strengths | Use Cases |
|----------|-----------|-----------|
| **OpenAI** | High quality, reliable | Professional content, DALL-E images |
| **Anthropic** | Long context, thoughtful | Analysis, technical content |
| **Grok** | Creative, real-time | Memes, unconventional content |
| **Gemini** | Google integration | Research, factual content |

## 📊 Performance

- **Response Time**: 15-45 seconds (including AI processing)
- **Scalability**: Horizontal scaling ready
- **Reliability**: 95%+ uptime with fallback systems
- **Resource Usage**: ~100MB memory, minimal CPU
- **Concurrent Requests**: 10+ simultaneous users

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (minimum requirement)
- Optional: Additional AI provider keys for enhanced features

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/braincargo/brain-blog.git
cd brain-blog

# 2. Configure environment
export OPENAI_API_KEY="sk-your-key-here"

# 3. Start the service
make docker-up

# 4. Test the service
curl http://localhost:8080/health
```

The service will be available at `http://localhost:8080`

## 📚 Documentation

### User Guides

- **[Getting Started](GETTING_STARTED.md)** - Complete setup and configuration guide
- **[Testing](TESTING.md)** - Comprehensive testing documentation
- **[Deployment](DEPLOYMENT.md)** - Production deployment strategies

### Technical Documentation

- **[Architecture](ARCHITECTURE.md)** - System design and multi-provider architecture
- **[Health Monitoring](HEALTH_MONITORING.md)** - Monitoring and observability
- **[Migration Guide](MIGRATION.md)** - OpenAI API migration reference

## 🔧 Configuration

### Basic Configuration

```yaml
# config/pipeline.yaml
providers:
  openai:
    api_key_env: "OPENAI_API_KEY"
    models:
      fast: "gpt-4o-mini"
      standard: "o3-pro"
      creative: "gpt-4o"

categories:
  technology:
    style_persona: "Paul Graham"
    provider_override: "anthropic"
  security:
    style_persona: "Bruce Schneier"
    provider_override: "openai"
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key

# Optional (for enhanced features)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GROK_API_KEY=xai-your-grok-key
GEMINI_API_KEY=your-gemini-key

# Storage (optional)
BLOG_POSTS_BUCKET=your-s3-bucket
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Vector Store Integration (optional)
OPENAI_VECTOR_STORE_IDS=vs_store_id1,vs_store_id2
ANTHROPIC_FILE_IDS=file_id1,file_id2,file_id3
```

## 🧠 Knowledge Base Integration

### Vector Store Support

The service supports knowledge base integration through vector stores:

- **OpenAI Vector Stores**: Upload documentation for enhanced context
- **Anthropic File Uploads**: Attach knowledge files to conversations
- **Automatic Detection**: Reads from manifest files created during upload
- **Selective Usage**: Configure when to use knowledge (blog generation vs. categorization)

### Setup Knowledge Base

```bash
# Install vector store dependencies
make vector-install

# Upload documentation to OpenAI vector store
make vector-upload-openai

# Upload files to Anthropic
make vector-upload-anthropic

# Upload to all providers
make vector-upload-all

# Check status
make vector-status
```

### Enhanced AI Capabilities

- **Company Knowledge**: AI has access to your specific documentation
- **Consistent Branding**: Maintains your voice and terminology
- **Technical Accuracy**: References your specifications and guidelines
- **Domain Expertise**: Provides context-aware responses

## 🧪 Testing

The service includes comprehensive testing:

- **Pipeline Architecture Tests**: 100% passing
- **Provider Integration Tests**: 13/13 passing  
- **Service Integration Tests**: 6/8 passing (2 require API keys)

```bash
# Quick test (no API keys required)
make test-quick

# Complete test suite
make test

# Test with your API keys
OPENAI_API_KEY=sk-... make test-complete
```

## 🚀 Deployment Options

### Docker (Recommended)

```bash
# Local development
make docker-up

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Platforms

The service is ready for deployment on:

- **AWS ECS/Fargate** - Container service
- **Google Cloud Run** - Serverless containers
- **Azure Container Instances** - Container platform
- **Kubernetes** - Any Kubernetes cluster

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment guides.

## 🔍 API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health` | GET | Service health check | `curl localhost:8080/health` |
| `/webhook` | POST | SMS webhook (Twilio) | Blog generation trigger |
| `/generate` | POST | Direct blog generation | JSON API for integrations |
| `/providers/status` | GET | AI provider status | Provider availability |

### Example API Usage

```bash
# Generate blog from URL
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'

# Check provider status
curl http://localhost:8080/providers/status
```

## 🔐 Security

### API Key Management

- Environment variable configuration
- No hardcoded secrets in code
- Support for secrets management services

### Network Security

- Localhost binding by default
- Configurable network exposure
- Support for reverse proxy deployment

### Input Validation

- URL validation and sanitization
- Phone number authorization (SMS)
- Request rate limiting ready

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality  
4. **Ensure** all tests pass
5. **Submit** a pull request

### Development Setup

```bash
# Install dependencies
make install

# Run tests
make test-quick

# Start development server
make docker-up

# View logs
make docker-logs
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Complete guides in the `docs/` directory
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and community support

### Troubleshooting

```bash
# Check service health
make docker-logs

# Verify environment
make env-check

# Run diagnostics
make test-quick

# Clean restart
make docker-clean && make docker-up
```

## 🌟 Features in Detail

### Intelligent Content Processing

- **Smart Categorization**: AI analyzes content and selects appropriate writing style
- **Style Adaptation**: Different personas for different content types (security, tech, crypto, etc.)
- **Brand Consistency**: Automatic BrainCargo branding and terminology

### Media Generation

- **Featured Images**: AI-generated professional images using DALL-E 3
- **Meme Creation**: Witty, relevant memes for engagement
- **Permanent Storage**: Automatic S3 upload with CDN-ready URLs

### Enterprise Features

- **Health Monitoring**: Kubernetes-ready health checks
- **Observability**: Structured logging and metrics
- **Scalability**: Stateless design for horizontal scaling
- **Reliability**: Multi-provider fallbacks and error recovery

## 🎯 Use Cases

### Content Marketing

- **Automated Blog Creation**: Transform articles into branded blog posts
- **Social Media Content**: Generate engaging posts with images and memes
- **SEO Optimization**: Structured content with proper formatting

### Developer Integration

- **API-First Design**: REST API for integration with existing systems
- **Webhook Support**: SMS and webhook triggers for automation
- **Container Deployment**: Easy integration into existing infrastructure

### Media Companies

- **Content Syndication**: Transform competitor content into original posts
- **Multi-Format Output**: Blog posts, social media, newsletters
- **Brand Voice Consistency**: Configurable writing styles and personas

## 📈 Roadmap

### Short Term

- Enhanced image generation with more providers
- Advanced SEO optimization features
- Real-time content updates

### Medium Term

- Multi-language support
- Advanced analytics and reporting
- A/B testing for content optimization

### Long Term

- AI-powered content strategy recommendations
- Enterprise SSO integration
- Advanced customization and white-labeling

---

**Ready to transform your content creation with AI? Get started in minutes with our comprehensive setup guide!**

*Built with ❤️ for the open source community* 