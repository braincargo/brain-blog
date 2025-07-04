#!/bin/bash

# BrainCargo Blog Service - Distribution Package Preparation
set -e

echo "📦 Preparing BrainCargo Blog Service distribution package..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
DIST_DIR="blog-service-docker"
VERSION=${1:-"latest"}

# Clean up any existing distribution
if [ -d "$DIST_DIR" ]; then
    echo "🧹 Cleaning up existing distribution..."
    rm -rf "$DIST_DIR"
fi

# Create distribution directory
mkdir -p "$DIST_DIR"

print_status "Created distribution directory: $DIST_DIR"

# Copy essential files
echo "📁 Copying distribution files..."

# Main configuration files
cp docker-compose.yml "$DIST_DIR/"
cp README.docker.md "$DIST_DIR/README.md"

# Configuration templates
mkdir -p "$DIST_DIR/config"
cp config/environment.example "$DIST_DIR/config/"
cp config/pipeline.example.yaml "$DIST_DIR/config/"

# Scripts
mkdir -p "$DIST_DIR/scripts"
cp scripts/setup.sh "$DIST_DIR/scripts/"
chmod +x "$DIST_DIR/scripts/setup.sh"

# Create placeholder directories
mkdir -p "$DIST_DIR/prompts/blog_generation"
mkdir -p "$DIST_DIR/prompts/categorization"
mkdir -p "$DIST_DIR/prompts/image_generation"
mkdir -p "$DIST_DIR/prompts/meme_generation"
mkdir -p "$DIST_DIR/vector_store_docs"
mkdir -p "$DIST_DIR/openai_store"
mkdir -p "$DIST_DIR/output"

# Create README files for empty directories
cat > "$DIST_DIR/vector_store_docs/README.md" << 'EOF'
# Vector Store Documents

Add your knowledge base documents here:

- **Supported formats**: .txt, .md, .pdf
- **OpenAI**: All text formats supported
- **Anthropic**: .txt and .pdf only
- **Max file size**: 500MB per file

After adding documents, run:
```bash
docker-compose exec braincargo-blog make vector-upload-all
```
EOF

cat > "$DIST_DIR/prompts/README.md" << 'EOF'
# Custom Prompts

The Docker image includes working default prompts. 

To customize prompts:
1. Copy the defaults from the container:
   ```bash
   docker-compose exec braincargo-blog cp -r /app/prompts/* ./prompts/
   ```

2. Edit the prompt files in each subdirectory

3. Restart the service:
   ```bash
   docker-compose restart
   ```

## Prompt Types
- `blog_generation/` - Blog post creation prompts
- `categorization/` - Content categorization prompts  
- `image_generation/` - Featured image generation prompts
- `meme_generation/` - Meme creation prompts
EOF

cat > "$DIST_DIR/output/README.md" << 'EOF'
# Generated Content Output

This directory will contain:
- `*.json` - Blog post data files
- `*.html` - Generated blog post HTML
- `images/` - Generated featured images

Files are automatically saved here when you generate content.
EOF

# Create .gitignore for the distribution
cat > "$DIST_DIR/.gitignore" << 'EOF'
# Environment and secrets
config/.env
*.env

# Generated content
output/*
!output/README.md

# Vector store data
openai_store/*.json
vector_store_docs/*
!vector_store_docs/README.md

# Logs
*.log
logs/

# Docker volumes
.data/

# OS
.DS_Store
Thumbs.db
EOF

# Create license file
cat > "$DIST_DIR/LICENSE" << 'EOF'
# BrainCargo Blog Service License

[Add your license text here]
EOF

# Create version file
echo "$VERSION" > "$DIST_DIR/VERSION"

print_status "Copied all distribution files"

# Create distribution archive
echo "📦 Creating distribution archive..."
tar -czf "braincargo-blog-service-${VERSION}.tar.gz" "$DIST_DIR"

print_status "Created distribution archive: braincargo-blog-service-${VERSION}.tar.gz"

# Generate release notes
cat > "RELEASE_NOTES_${VERSION}.md" << EOF
# BrainCargo Blog Service v${VERSION}

## 🚀 Quick Start

1. **Download and extract:**
   \`\`\`bash
   wget https://github.com/braincargo/blog-service-docker/releases/download/v${VERSION}/braincargo-blog-service-${VERSION}.tar.gz
   tar -xzf braincargo-blog-service-${VERSION}.tar.gz
   cd blog-service-docker
   \`\`\`

2. **Setup and start:**
   \`\`\`bash
   ./scripts/setup.sh
   nano config/.env  # Add your API keys
   docker-compose up -d
   \`\`\`

3. **Test:**
   \`\`\`bash
   curl http://localhost:8080/health
   \`\`\`

## 📋 What's Included

- ✅ Docker Compose configuration
- ✅ Automated setup script
- ✅ Configuration templates
- ✅ Vector store support
- ✅ Custom prompt support
- ✅ Comprehensive documentation

## 🔧 Requirements

- Docker and Docker Compose
- OpenAI API key (minimum)
- Optional: Anthropic, Grok, Gemini API keys

## 📚 Documentation

See the included README.md for complete setup and usage instructions.

## 🆘 Support

- GitHub Issues: https://github.com/braincargo/blog-service/issues
- Documentation: https://docs.braincargo.com
EOF

print_status "Generated release notes: RELEASE_NOTES_${VERSION}.md"

echo ""
echo "🎉 Distribution package ready!"
echo ""
echo "📦 Files created:"
echo "  - $DIST_DIR/ (distribution directory)"
echo "  - braincargo-blog-service-${VERSION}.tar.gz (archive)"
echo "  - RELEASE_NOTES_${VERSION}.md (release notes)"
echo ""
echo "📤 Next steps:"
echo "  1. Test the distribution:"
echo "     cd $DIST_DIR && ./scripts/setup.sh"
echo ""
echo "  2. Build and push Docker image:"
echo "     make docker-dist-release VERSION=${VERSION}"
echo ""
echo "  3. Upload archive to GitHub releases"
echo "     Upload: braincargo-blog-service-${VERSION}.tar.gz"
echo ""
print_warning "Don't forget to update the Docker Hub image with: make docker-dist-release VERSION=${VERSION}" 