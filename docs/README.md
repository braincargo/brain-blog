# Documentation

> **Documentation navigation for the BrainCargo Blog Service**

This directory contains comprehensive documentation for the BrainCargo Blog Service. For a quick project overview, see the [main README](../README.md).

## 📚 Documentation Index

### 🚀 Getting Started
- **[Project Overview](PROJECT_OVERVIEW.md)** - Detailed project introduction and features
- **[Getting Started](GETTING_STARTED.md)** - Complete setup guide for local development and Docker

### 🏗️ Technical Documentation
- **[Architecture](ARCHITECTURE.md)** - System design, multi-provider architecture, and media generation
- **[Testing](TESTING.md)** - Comprehensive testing guide and test coverage
- **[Vector Stores](VECTOR_STORES.md)** - Knowledge base integration with OpenAI and Anthropic
- **[Migration Guide](MIGRATION.md)** - OpenAI API migration reference (Assistants → Responses)

### 🚀 Operations & Deployment
- **[Deployment](DEPLOYMENT.md)** - Production deployment strategies for cloud platforms
- **[Health Monitoring](HEALTH_MONITORING.md)** - Health checks, monitoring, and observability

## 🎯 Quick Navigation

### New to the Project?
1. **[Main README](../README.md)** - Start here for project overview
2. **[Getting Started](GETTING_STARTED.md)** - Set up your development environment
3. **[Testing](TESTING.md)** - Run tests to ensure everything works

### Ready to Deploy?
1. **[Architecture](ARCHITECTURE.md)** - Understand the system design
2. **[Deployment](DEPLOYMENT.md)** - Production deployment guide
3. **[Health Monitoring](HEALTH_MONITORING.md)** - Set up monitoring

### Need Technical Details?
- **Multi-Provider AI Support**: [Architecture](ARCHITECTURE.md#provider-system)
- **Pipeline Processing**: [Architecture](ARCHITECTURE.md#pipeline-flow)
- **Media Generation**: [Architecture](ARCHITECTURE.md#media-generation-system)
- **Error Handling**: [Architecture](ARCHITECTURE.md#error-handling--resilience)

## 🛠️ Quick Commands

```bash
# Start development
export OPENAI_API_KEY="sk-your-key-here"
make docker-up

# Run tests
make test-quick

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8080/health
```

## 📖 Documentation Overview

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Project Overview](PROJECT_OVERVIEW.md)** | Complete feature overview | Everyone |
| **[Getting Started](GETTING_STARTED.md)** | Setup and configuration | Developers |
| **[Architecture](ARCHITECTURE.md)** | System design details | Developers/Architects |
| **[Testing](TESTING.md)** | Testing guide and best practices | Developers |
| **[Vector Stores](VECTOR_STORES.md)** | Knowledge base integration | Developers/Content Teams |
| **[Deployment](DEPLOYMENT.md)** | Production deployment | DevOps/SRE |
| **[Health Monitoring](HEALTH_MONITORING.md)** | Monitoring and observability | DevOps/SRE |
| **[Migration Guide](MIGRATION.md)** | API migration reference | Developers |

---

**📋 For the main project information, see the [root README](../README.md)** 