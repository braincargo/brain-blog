# Vector Store Integration Guide

> **Enhanced AI capabilities through knowledge base integration**

## 🧠 Overview

The BrainCargo Blog Service supports knowledge base integration through vector stores, allowing AI providers to access your company's documentation, guidelines, and domain expertise for more accurate and contextually relevant content generation.

The system uses generic, reusable components that can be adapted for any organization:
- **Generic file naming**: `openai_vector_store.py` instead of company-specific names
- **Configurable knowledge base names**: Default to `braincargo_knowledge` but easily customizable
- **Flexible directory structure**: Use `vector_store_docs/` for knowledge files
- **Universal manifest format**: Standard JSON files for tracking uploads

## 🎯 Benefits

### Enhanced AI Capabilities
- **Company Knowledge**: AI has access to your specific documentation
- **Consistent Branding**: Maintains your voice and terminology  
- **Technical Accuracy**: References your specifications and guidelines
- **Domain Expertise**: Provides context-aware responses

### Supported Providers
- **OpenAI Vector Stores**: Document embeddings with semantic search
- **Anthropic File Uploads**: Direct file attachment to conversations

## 📋 Prerequisites

- At least one AI provider API key (OpenAI or Anthropic)
- Documentation files in supported formats
- Vector store dependencies installed

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install vector store upload tools
make vector-install
```

### 2. Prepare Knowledge Files

Create a `vector_store_docs/` directory with your knowledge files:

```bash
# Create vector_store_docs directory
mkdir vector_store_docs

# Add your knowledge files
# Supported formats: .md, .txt, .pdf, .json
cp your-company-docs/* vector_store_docs/
```

### Supported File Types

| Format | Extension | Use Case |
|--------|-----------|----------|
| **Markdown** | `.md` | Documentation, guides, technical specs |
| **Text** | `.txt` | Plain text knowledge, FAQs |
| **PDF** | `.pdf` | Manuals, whitepapers, reports |  
| **JSON** | `.json` | Structured data, configurations |

### 3. Upload to Vector Stores

#### Upload to OpenAI Vector Store

```bash
# Upload all docs to OpenAI vector store
make vector-upload-openai

# Manual upload using script directly
cd openai_store
python3 openai_vector_store.py --dir ../vector_store_docs --name your_knowledge_base

# Check upload status
make vector-status
```

#### Upload to Anthropic

```bash
# Upload files to Anthropic
make vector-upload-anthropic

# Check upload status  
make vector-status
```

#### Upload to All Providers

```bash
# Upload to all available providers
make vector-upload-all
```

## 📊 Configuration

### Vector Store Settings

The vector store configuration is in `config/pipeline.yaml`:

```yaml
# Vector Store Configuration
vector_stores:
  enabled: true  # Enable knowledge base integration
  
  openai:
    enabled: true
    vector_store_ids: "${OPENAI_VECTOR_STORE_IDS}"  # Auto-detected
    manifest_file: "openai_store/openai_vector_store.json"
    auto_detect: true
  
  anthropic:
    enabled: true
    file_ids: "${ANTHROPIC_FILE_IDS}"  # Auto-detected
    manifest_file: "openai_store/anthropic_uploads.json"
    auto_detect: true
  
  # When to use knowledge files
  usage:
    blog_generation: true     # Use for content generation
    categorization: false     # Keep categorization fast
    image_generation: false   # Keep image prompts creative
    meme_generation: false    # Keep memes fast
```

### Environment Variables

Set these environment variables for manual vector store configuration:

```bash
# OpenAI Vector Store IDs (optional - auto-detected from manifest)
export OPENAI_VECTOR_STORE_IDS="vs_store_id1,vs_store_id2"

# Anthropic File IDs (optional - auto-detected from manifest)  
export ANTHROPIC_FILE_IDS="file_id1,file_id2,file_id3"
```

## 🔍 Usage Examples

### Blog Generation with Knowledge

When vector stores are configured, the AI will automatically use your knowledge files during blog generation:

```bash
# Generate blog - automatically uses knowledge base
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### Check Vector Store Status

```bash
# View vector store status and uploaded files
make vector-status
```

Expected output:
```
📊 Vector Store Status...

🗂️ Local vector_store_docs directory:
vector_store_docs/company-overview.md
vector_store_docs/technical-specifications.pdf
vector_store_docs/brand-guidelines.txt

📋 Total files: 15

🤖 OpenAI Vector Store:
{
  "vector_store_id": "vs_abc123...",
  "file_ids": ["file_123", "file_456", "file_789"]
}

🧠 Anthropic Uploads:
{
  "uploaded_files": [
    {
      "id": "file_anthropic_123",
      "filename": "company-overview.md",
      "size_bytes": 5420
    }
  ],
  "total_files": 8
}
```

## 🔧 Advanced Configuration

### Selective Knowledge Usage

Configure when to use knowledge files in `config/pipeline.yaml`:

```yaml
vector_stores:
  usage:
    blog_generation: true     # ✅ Use for main content
    categorization: false     # ❌ Keep fast, don't use knowledge
    image_generation: false   # ❌ Keep creative, don't constrain
    meme_generation: false    # ❌ Keep spontaneous
```

### Provider-Specific Configuration

#### OpenAI Vector Store Configuration

```yaml
providers:
  openai:
    # Vector store will be auto-detected from manifest
    # Or set manually via environment variable
```

#### Anthropic File Configuration

```yaml
providers:
  anthropic:
    # File IDs will be auto-detected from manifest
    # Or set manually via environment variable
```

## 📈 Best Practices

### Document Organization

```
vector_store_docs/
├── company/
│   ├── mission-vision.md
│   ├── brand-guidelines.pdf
│   └── style-guide.txt
├── technical/
│   ├── api-specifications.md
│   ├── architecture-overview.pdf
│   └── security-policies.txt
└── products/
    ├── feature-descriptions.md
    ├── user-guides.pdf
    └── faq.txt
```

### File Naming Conventions

- Use descriptive, consistent naming
- Include version numbers for evolving documents  
- Separate by domain (technical, marketing, legal)
- Keep file sizes reasonable (<10MB per file)

### Content Guidelines

- **Be Specific**: Include detailed, actionable information
- **Stay Current**: Update documents regularly
- **Use Clear Language**: Write for AI and human readability
- **Include Context**: Provide background and use cases
- **Reference Standards**: Link to official specifications

## 🛠️ Troubleshooting

### Common Issues

#### No Vector Store Found
```
⚠️ No OpenAI vector store ID found. Run 'make vector-upload-openai' to create one.
```
**Solution**: Upload documents to create vector store
```bash
make vector-upload-openai
```

#### Upload Failed
```
❌ Failed to upload docs/large-file.pdf: File too large
```
**Solution**: Check file size limits and format support
- OpenAI: Max 512MB per file
- Anthropic: Max 25MB per file

#### No Knowledge Files Found
```
⚠️ No Anthropic knowledge files found. Run 'make vector-upload-anthropic' to upload files.
```
**Solution**: Upload files to Anthropic
```bash
make vector-upload-anthropic
```

### Debug Commands

```bash
# Check vector_store_docs directory
ls -la vector_store_docs/

# Verify manifest files exist
ls -la openai_store/

# Check file permissions
find vector_store_docs/ -type f ! -readable

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/vector_stores
```

## 🔄 Updating Knowledge Base

### Adding New Documents

```bash
# Add new files to vector_store_docs directory
cp new-documents/* vector_store_docs/

# Re-upload to update vector stores
make vector-upload-all

# Verify updates
make vector-status
```

### Removing Documents

```bash
# Remove files from vector_store_docs directory
rm vector_store_docs/outdated-document.pdf

# Re-upload to sync changes
make vector-upload-all
```

### Version Management

```bash
# Create versioned docs
mkdir vector_store_docs/v2.0/
cp updated-specs/* vector_store_docs/v2.0/

# Upload new version
make vector-upload-all
```

## 📊 Monitoring & Analytics

### Upload Metrics

The system tracks:
- Number of files uploaded
- Total size of knowledge base
- Upload success/failure rates
- Last update timestamps

### Usage Analytics  

Monitor knowledge base usage:
- How often knowledge files are referenced
- Which documents are most useful
- Provider-specific usage patterns

## 🔐 Security Considerations

### Data Privacy

- **Encrypted Transit**: All uploads use HTTPS
- **Provider Security**: Data stored according to provider policies
- **Access Control**: API keys control access to knowledge bases

### Sensitive Information

- Review documents before uploading
- Remove sensitive data (passwords, keys, PII)
- Use environment-specific knowledge bases
- Consider data retention policies

## 🚀 Next Steps

1. **Upload Your Documentation**: Start with `make vector-upload-all`
2. **Test Knowledge Integration**: Generate a blog post and verify context usage
3. **Optimize Configuration**: Adjust usage settings based on results
4. **Monitor Performance**: Track how knowledge base affects response quality
5. **Iterate and Improve**: Regularly update and refine your knowledge base

---

**🧠 Ready to supercharge your AI with company knowledge? Start with `make vector-install`!** 

# Testing and Verification

## Unit Tests

Run vector store unit tests to verify provider integration:

```bash
make test-vector-stores
```

These tests verify:
- Vector store methods exist in providers
- Configuration parsing works correctly
- Manifest file handling is functional
- Provider detection works as expected

## Integration Testing

For complete end-to-end testing with real API calls:

```bash
make test-vector-integration
```

This integration test (`tests/test_vector_store_integration.py`):
1. Creates test documents in `vector_store_docs/`
2. Uploads documents to OpenAI vector store
3. Uploads documents to Anthropic (if API key available)
4. Tests blog generation with knowledge integration
5. Verifies that knowledge is actually being used

**Requirements for integration testing:**
- `OPENAI_API_KEY` environment variable (required)
- `ANTHROPIC_API_KEY` environment variable (optional)
- Internet connection for API calls

## Manual Verification

### 1. Check Vector Store Status
```bash
make vector-status
```

This shows:
- Local documents in `vector_store_docs/`
- OpenAI vector store manifest
- Anthropic upload manifest

### 2. Test Blog Generation
Generate a blog post and verify knowledge usage:

```bash
# Start the service
make docker-up

# Generate a blog about your company/knowledge
curl -X POST http://localhost:8080/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Write about our recent technical achievements and expertise",
    "provider": "openai"
  }'
```

Look for mentions of your specific knowledge in the generated content.

### 3. Check Logs
Monitor provider behavior:

```bash
make docker-logs
```

Look for vector store related log messages:
- `Vector store ID detected: vs_xxxxx`
- `Using knowledge files for generation`
- `Added file_search tool to request`

## Troubleshooting Tests

### Common Issues

**Unit Tests Failing:**
```bash
# Check if providers can be imported
python3 -c "from providers.openai_provider import OpenAIProvider; print('✅ OpenAI provider OK')"
python3 -c "from providers.anthropic_provider import AnthropicProvider; print('✅ Anthropic provider OK')"
```

**Integration Tests Failing:**
```bash
# Verify API keys
make env-check

# Check upload scripts
ls -la openai_store/
python3 openai_store/openai_vector_store.py --help
```

**No Knowledge Usage:**
```bash
# Verify vector store configuration
cat config/pipeline.yaml | grep -A 10 vector_stores

# Check manifest files
cat openai_store/openai_vector_store.json
cat openai_store/anthropic_uploads.json
```

### Debug Mode

For detailed debugging, run tests with verbose output:

```bash
# Unit tests with verbose output
python3 tests/test_vector_stores.py -v

# Integration test with debug info
PYTHONPATH=. python3 tests/test_vector_store_integration.py
```

## Test Data

The integration test creates these sample documents:

1. **braincargo_knowledge.txt** - Company overview and technologies
2. **technical_guidelines.txt** - Architecture principles and best practices  
3. **company_projects.txt** - Project descriptions and achievements

You can also create your own test documents in `vector_store_docs/` for testing with your specific knowledge.

## Automated Testing

Vector store tests are included in the main test suite:

```bash
# Runs unit tests (no API calls)
make test-standalone

# Full test suite including integration
make test
```

The tests will automatically skip integration testing if API keys are not available. 