#!/bin/bash

# BrainCargo Blog Service Docker Setup Script
set -e

echo "🚀 Setting up BrainCargo Blog Service..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p config
mkdir -p prompts/{blog_generation,categorization,image_generation,meme_generation}
mkdir -p vector_store_docs
mkdir -p openai_store
mkdir -p output

print_status "Created directory structure"

# Copy configuration templates if they don't exist
if [ ! -f "config/.env" ]; then
    if [ -f "config/environment.example" ]; then
        cp config/environment.example config/.env
        print_status "Created config/.env from template"
        print_warning "IMPORTANT: Edit config/.env with your API keys!"
    else
        print_error "Template file config/environment.example not found"
        echo "# Add your API keys here" > config/.env
        echo "OPENAI_API_KEY=your_openai_api_key_here" >> config/.env
        print_warning "Created basic config/.env - add your API keys!"
    fi
else
    print_status "config/.env already exists"
fi

if [ ! -f "config/pipeline.yaml" ]; then
    if [ -f "config/pipeline.example.yaml" ]; then
        cp config/pipeline.example.yaml config/pipeline.yaml
        print_status "Created config/pipeline.yaml from template"
    else
        print_error "Template file config/pipeline.example.yaml not found"
        exit 1
    fi
else
    print_status "config/pipeline.yaml already exists"
fi

# Set proper permissions
chmod 755 output openai_store
chmod 644 config/.env config/pipeline.yaml 2>/dev/null || true

print_status "Set file permissions"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in current directory"
    echo "Please ensure you're in the correct directory with docker-compose.yml"
    exit 1
fi

# Validate Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Edit your API keys:"
echo "   nano config/.env"
echo ""
echo "2. Customize configuration (optional):"
echo "   nano config/pipeline.yaml"
echo ""
echo "3. Add custom prompts (optional):"
echo "   # Copy your custom prompts to prompts/ directory"
echo "   # The service includes working defaults if you don't customize"
echo ""
echo "4. Add knowledge documents (optional):"
echo "   # Copy your documents to vector_store_docs/"
echo "   # Supported formats: .txt, .md, .pdf"
echo ""
echo "5. Start the service:"
echo "   docker-compose up -d"
echo ""
echo "6. Upload vector store documents (if added):"
echo "   docker-compose exec braincargo-blog make vector-upload-all"
echo ""
echo "7. Check service health:"
echo "   curl http://localhost:8080/health"
echo ""
echo "8. Generate your first blog post:"
echo "   curl -X POST http://localhost:8080/generate-blog \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"topic\": \"AI trends in 2024\", \"provider\": \"openai\"}'"
echo ""
print_warning "Remember to add your API keys to config/.env before starting!" 