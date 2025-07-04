# 🚀 BrainCargo Blog Service - Docker Edition

The BrainCargo Blog Service is a powerful AI-driven content generation platform that creates engaging blog posts, images, and memes using multiple AI providers with customizable prompts and knowledge bases.

## 🎯 Quick Start (5 minutes)

1. **Download the service:**
   ```bash
   git clone https://github.com/braincargo/brain-blog.git
   cd brain-blog
   ```

2. **Initialize configuration:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Add your API keys:**
   ```bash
   nano config/.env
   # Add at minimum: OPENAI_API_KEY=your_key_here
   ```

4. **Start the service:**
   ```bash
   docker-compose up -d
   ```

5. **Test it works:**
   ```bash
   curl http://localhost:8080/health
   ```

6. **Generate your first blog post:**
   ```bash
   curl -X POST http://localhost:8080/generate-blog \
     -H 'Content-Type: application/json' \
     -d '{"topic": "The future of AI", "provider": "openai"}'
   ```

## 📁 Directory Structure

```
brain-blog/
├── docker-compose.yml           # Service orchestration
├── config/
│   ├── .env                     # Your API keys (create from template)
│   ├── pipeline.yaml            # Service configuration (create from template)
│   ├── environment.example      # Template for .env
│   └── pipeline.example.yaml    # Template for pipeline.yaml
├── prompts/                     # Custom prompts (optional)
│   ├── blog_generation/
│   ├── categorization/
│   ├── image_generation/
│   └── meme_generation/
├── vector_store_docs/           # Your knowledge documents (optional)
├── openai_store/                # Vector store manifests (auto-generated)
├── output/                      # Generated content output
└── scripts/
    └── setup.sh                 # Initial setup script
```

## 🔧 Configuration

### Environment Variables (config/.env)

**Required:**
- `OPENAI_API_KEY` - For blog generation and vector stores

**Optional AI Providers:**
- `ANTHROPIC_API_KEY` - Claude models
- `GROK_API_KEY` - Grok models  
- `GEMINI_API_KEY` - Gemini models

**Optional Cloud Storage:**
- `BLOG_POSTS_BUCKET` - AWS S3 bucket for output
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

### Pipeline Configuration (config/pipeline.yaml)

The pipeline configuration controls:
- AI provider preferences and fallbacks
- Model selections for different tasks
- Vector store settings
- Rate limiting and timeouts

Edit `config/pipeline.yaml` to customize these settings.

## 🧠 Knowledge Base (Vector Store)

### Adding Documents

1. **Add your documents:**
   ```bash
   cp your-documents/* vector_store_docs/
   # Supported: .txt, .md, .pdf files
   ```

2. **Upload to vector stores:**
   ```bash
   docker-compose exec brain-blog make vector-upload-all
   ```

3. **Check status:**
   ```bash
   docker-compose exec brain-blog make vector-status
   ```

### Document Requirements

- **OpenAI**: Supports .txt, .md, .pdf, and most text formats
- **Anthropic**: Supports .txt and .pdf only (markdown files will be converted)
- **Max file size**: 500MB per file
- **Total storage**: 100GB per organization

## ✍️ Custom Prompts

The service includes professional default prompts, but you can customize them:

### Blog Generation Prompts
```bash
# Copy default prompts (if not already present)
docker-compose exec brain-blog cp -r /app/prompts/blog_generation ./prompts/

# Edit prompts
nano prompts/blog_generation/base.txt
nano prompts/blog_generation/security_style.txt
nano prompts/blog_generation/tech_style.txt
nano prompts/blog_generation/web3_style.txt
```

### Other Prompt Types
- `prompts/categorization/main.txt` - Content categorization
- `prompts/image_generation/main.txt` - Featured image generation
- `prompts/meme_generation/main.txt` - Meme creation

**Note:** Restart the service after changing prompts: `docker-compose restart`

## 🔌 API Usage

### Generate Blog Post
```bash
curl -X POST http://localhost:8080/generate-blog \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "Your blog topic",
    "provider": "openai",
    "style": "technology",
    "use_knowledge": true
  }'
```

### Health Check
```bash
curl http://localhost:8080/health
```

### Vector Store Status
```bash
curl http://localhost:8080/vector-status
```

## 🐳 Docker Commands

### Service Management
```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Update to latest image
docker-compose pull && docker-compose up -d
```

### Accessing Container
```bash
# Open shell in container
docker-compose exec brain-blog bash

# Run specific commands
docker-compose exec brain-blog make vector-status
docker-compose exec brain-blog python -c "import sys; print(sys.path)"
```

## 📊 Monitoring

### Health Checks
The service includes automatic health checks. Check status:
```bash
docker-compose ps
```

### Logs
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific timeframe
docker-compose logs --since="1h"
```

### Output Files
Generated content is saved to the `output/` directory:
- `output/*.json` - Blog post data
- `output/*.html` - Blog post HTML
- `output/images/` - Generated images

## 🔒 Security Best Practices

1. **API Keys**: Never commit `.env` files to version control
2. **File Permissions**: The service runs as user 1000:1000 for security
3. **Network**: The service only exposes port 8080
4. **Updates**: Regularly update to the latest image version

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check if port 8080 is available
sudo lsof -i :8080

# Check Docker logs
docker-compose logs brain-blog

# Verify configuration
docker-compose config
```

### API Key Issues
```bash
# Verify environment variables are loaded
docker-compose exec brain-blog env | grep API_KEY

# Test API keys directly
docker-compose exec brain-blog python -c "
import os
print('OpenAI:', '✅' if os.environ.get('OPENAI_API_KEY') else '❌')
print('Anthropic:', '✅' if os.environ.get('ANTHROPIC_API_KEY') else '❌')
"
```

### Vector Store Issues
```bash
# Check vector store status
docker-compose exec brain-blog make vector-status

# Re-upload documents
docker-compose exec brain-blog make vector-upload-all

# Verify documents exist
docker-compose exec brain-blog ls -la vector_store_docs/
```

### Permission Issues
```bash
# Fix output directory permissions
sudo chown -R 1000:1000 output/ openai_store/

# Check container user
docker-compose exec brain-blog id
```

## 🔄 Updates

To update to the latest version:
```bash
docker-compose pull
docker-compose up -d
```

Your configuration and custom prompts will be preserved.

## 📖 Advanced Usage

### Multiple API Keys for Load Balancing
Add multiple keys separated by commas:
```env
OPENAI_API_KEY=key1,key2,key3
```

### Custom Model Selection
Edit `config/pipeline.yaml`:
```yaml
providers:
  openai:
    models:
      fast: gpt-4o-mini
      standard: gpt-4o
      creative: gpt-4o
```

### Rate Limiting
Adjust rate limits in `config/pipeline.yaml`:
```yaml
rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst_limit: 10
```

## 🆘 Support

- **Documentation**: [Full API documentation](https://docs.braincargo.com)
- **Issues**: [GitHub Issues](https://github.com/braincargo/blog-service/issues)
- **Community**: [Discord Server](https://discord.gg/braincargo)

## 📄 License

This software is licensed under [your license]. See LICENSE file for details.

---

**Ready to get started?** Run `./scripts/setup.sh` and follow the prompts! 🎉 