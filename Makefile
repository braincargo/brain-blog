# BrainCargo Blog Service Makefile
# Local testing and development commands

.PHONY: help test test-quick test-integration-only test-production test-complete test-blog test-standalone env-check install clean docker-build docker-up docker-down docker-restart docker-logs docker-clean vector-install vector-upload-openai vector-upload-anthropic vector-upload-all vector-status test-vector-stores test-vector-integration docker-publish docker-push docker-tag docker-release docker-test prepare-distribution

# Default target
help:
	@echo "🚀 BrainCargo Blog Service - Local Testing"
	@echo "==========================================="
	@echo ""
	@echo "Development commands:"
	@echo "  make env-check     - Check environment setup"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Start development server"
	@echo "  make clean         - Clean up test outputs"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test-unit     - Run unit tests (standalone)"
	@echo "  make test-all      - Run all tests in tests directory (standalone)"
	@echo "  make test-module   - Run specific test module (standalone)"
	@echo "  make test-complete - Run complete pipeline tests (standalone)"
	@echo "  make test-blog     - Generate a test blog post (standalone)"
	@echo "  make test-standalone - Run all tests except integration (no Docker needed)"
	@echo ""
	@echo "Testing with Docker (auto-managed, fast models):"
	@echo "  make test-quick    - Integration tests (starts/stops Docker, uses fast models)"
	@echo "  make test          - All tests (starts/stops Docker, uses fast models)"
	@echo ""
	@echo "Manual Docker testing:"
	@echo "  make test-integration-only - Integration tests (Docker must be running)"
	@echo "  make test-production       - Full tests with production models (slower)"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker Compose services"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make docker-restart- Restart Docker Compose services"
	@echo "  make docker-logs   - View Docker Compose logs"
	@echo "  make docker-clean  - Stop services and clean up Docker resources"
	@echo ""
	@echo "Vector Store commands:"
	@echo "  make vector-install       - Install vector store dependencies"
	@echo "  make vector-upload-openai - Upload docs to OpenAI vector store"
	@echo "  make vector-upload-anthropic - Upload docs to Anthropic"
	@echo "  make vector-upload-all    - Upload docs to all available providers"
	@echo "  make vector-status        - Show vector store status and files"
	@echo "  make test-vector-stores   - Test vector store functionality"
	@echo "  make test-vector-integration - Run vector store integration test"
	@echo ""
	@echo "Docker publishing commands:"
	@echo "  make docker-push          - Build and push Docker image to Docker Hub"
	@echo "  make docker-tag VERSION=x.x.x - Build and tag image with version"
	@echo "  make docker-release VERSION=x.x.x - Build, tag, and push versioned release"
	@echo "  make docker-test          - Test Docker image"
	@echo ""
	@echo "Docker Hub customization:"
	@echo "  DOCKER_USER=yourusername  - Use your Docker Hub username (default: braincargo)"
	@echo "  IMAGE_NAME=yourname       - Custom image name (default: brain-blog)"
	@echo "  Example: make docker-push DOCKER_USER=yourusername"
	@echo "  make prepare-distribution - Create distribution package for release"
	@echo ""
	@echo "Requirements:"
	@echo "  - OPENAI_API_KEY environment variable"
	@echo "  - Optional: ANTHROPIC_API_KEY, GROK_API_KEY, GEMINI_API_KEY"
	@echo "  - For vector stores: vector_store_docs/ directory with knowledge files"

# Check environment setup
env-check:
	@echo "🔧 Checking environment setup..."
	@python3 -c "import os; print('✅ OPENAI_API_KEY:', '***' if os.environ.get('OPENAI_API_KEY') else '❌ NOT SET')"
	@python3 -c "import os; print('⚠️ ANTHROPIC_API_KEY:', '***' if os.environ.get('ANTHROPIC_API_KEY') else 'Not set (optional)')"
	@python3 -c "import os; print('⚠️ GROK_API_KEY:', '***' if os.environ.get('GROK_API_KEY') else 'Not set (optional)')"
	@python3 -c "import os; print('⚠️ GEMINI_API_KEY:', '***' if os.environ.get('GEMINI_API_KEY') else 'Not set (optional)')"
	@python3 -c "import os; print('⚠️ BLOG_POSTS_BUCKET:', os.environ.get('BLOG_POSTS_BUCKET', 'Not set (optional)'))"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Run integration tests with full Docker lifecycle
test-quick:
	@echo "🏃‍♂️ Running integration tests with Docker (TEST MODE - Fast Models)..."
	@echo "🐳 Stopping any existing Docker services..."
	@docker-compose down 2>/dev/null || true
	@echo "🐳 Starting fresh Docker services with test mode..."
	@ENABLE_TEST_MODE=true docker-compose up -d
	@echo "⏳ Waiting for service to be ready..."
	@sleep 10
	@echo "🧪 Running integration tests..."
	@python3 tests/test_local.py || (echo "❌ Tests failed, cleaning up Docker..." && docker-compose down && exit 1)
	@echo "🐳 Stopping Docker services..."
	@docker-compose down
	@echo "✅ Integration tests completed with Docker cleanup"

# Run integration tests (assumes Docker is already running)
test-integration-only:
	@echo "🧪 Running integration tests (Docker must be running)..."
	@python3 tests/test_local.py

# Run tests with production models (slower but realistic)
test-production:
	@echo "🧪 Running complete test suite with Docker (PRODUCTION MODELS - Slower)..."
	@echo "🐳 Stopping any existing Docker services..."
	@docker-compose down 2>/dev/null || true
	@echo "🐳 Starting fresh Docker services with production models..."
	@docker-compose up -d
	@echo "⏳ Waiting for service to be ready..."
	@sleep 10
	@echo "🧪 Running integration tests with production models..."
	@python3 tests/test_local.py || (echo "❌ Tests failed, cleaning up Docker..." && docker-compose down && exit 1)
	@echo "🐳 Stopping Docker services..."
	@docker-compose down
	@echo "✅ Production model tests completed with Docker cleanup"

# Run complete pipeline tests
test-complete:
	@echo "🧪 Running complete pipeline tests..."
	python3 tests/test_complete_pipeline.py

# Generate a test blog post
test-blog:
	@echo "📝 Generating test blog post..."
	python3 tests/test_blog_generation.py

# Run unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	python3 tests/run_tests.py

# Run all tests in the tests directory
test-all:
	@echo "🧪 Running all tests..."
	python3 tests/run_tests.py --all

# Run specific test module
test-module:
	@echo "🧪 Running specific test module..."
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Please specify MODULE=<module_name>"; \
		echo "Example: make test-module MODULE=test_config"; \
	else \
		python3 tests/run_tests.py --module $(MODULE); \
	fi

# Run all tests (requires Docker)
test: 
	@echo "🧪 Running complete test suite with Docker (TEST MODE - Fast Models)..."
	@echo "🐳 Stopping any existing Docker services..."
	@docker-compose down 2>/dev/null || true
	@echo "🐳 Starting fresh Docker services with test mode..."
	@ENABLE_TEST_MODE=true docker-compose up -d
	@echo "⏳ Waiting for service to be ready..."
	@sleep 10
	@echo "🔧 Running environment check..."
	@$(MAKE) env-check
	@echo "🧪 Running unit tests..."
	@$(MAKE) test-unit
	@echo "🧪 Running integration tests..."
	@python3 tests/test_local.py || (echo "❌ Integration tests failed, cleaning up Docker..." && docker-compose down && exit 1)
	@echo "🧪 Running pipeline tests..."
	@ENABLE_TEST_MODE=true $(MAKE) test-complete
	@echo "📝 Running blog generation tests..."
	@ENABLE_TEST_MODE=true $(MAKE) test-blog
	@echo "🐳 Stopping Docker services..."
	@docker-compose down
	@echo ""
	@echo "🎉 All tests completed with Docker cleanup!"
	@echo "Check the local_output/ directory for generated blog posts."

# Run unit tests only (no Docker required)
test-standalone: env-check test-unit test-complete test-blog test-vector-stores
	@echo ""
	@echo "🎉 Standalone tests completed!"
	@echo "Note: Integration tests (test-quick) skipped - run 'make docker-up' first if needed"

# Clean up test outputs
clean:
	@echo "🧹 Cleaning up test outputs..."
	rm -rf local_output/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf tests/.pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Cleanup complete"

# Development server (if needed)
dev:
	@echo "🚀 Starting development server..."
	python3 app.py

# Docker: Build the image
docker-build:
	@echo "🐳 Building Docker image..."
	docker-compose build

# Docker: Start services
docker-up:
	@echo "🐳 Starting Docker Compose services..."
	docker-compose up -d
	@echo "✅ Services started. Check logs with: make docker-logs"
	@echo "🌐 Service available at: http://localhost:8080"
	@echo "🏥 Health check: http://localhost:8080/health"

# Docker: Stop services
docker-down:
	@echo "🐳 Stopping Docker Compose services..."
	docker-compose down
	@echo "✅ Services stopped"

# Docker: Restart services
docker-restart:
	@echo "🐳 Restarting Docker Compose services..."
	docker-compose restart
	@echo "✅ Services restarted"

# Docker: View logs
docker-logs:
	@echo "📋 Viewing Docker Compose logs..."
	docker-compose logs -f

# Docker: View logs for specific service
docker-logs-service:
	@echo "📋 Viewing logs for braincargo-blog-service..."
	docker-compose logs -f braincargo-blog-service

# Docker: Clean up everything
docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down --volumes --remove-orphans
	docker system prune -f
	@echo "✅ Docker cleanup complete"

# Docker: Full rebuild and start
docker-rebuild:
	@echo "🔄 Full Docker rebuild and start..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Full rebuild complete. Service available at: http://localhost:8080"

# Docker: Show status
docker-status:
	@echo "📊 Docker Compose services status..."
	docker-compose ps

# Vector Store: Install dependencies
vector-install:
	@echo "📦 Installing vector store dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Vector store dependencies installed"

# Vector Store: Upload documents to OpenAI vector store
vector-upload-openai:
	@echo "🔄 Uploading documents to OpenAI vector store..."
	@if [ ! -d "vector_store_docs" ]; then \
		echo "❌ vector_store_docs/ directory not found. Create vector_store_docs/ and add your knowledge files."; \
		exit 1; \
	fi
	@cd openai_store && python3 openai_vector_store.py --dir ../vector_store_docs --name braincargo_knowledge
	@echo "✅ Documents uploaded to OpenAI vector store"

# Vector Store: Upload documents to Anthropic
vector-upload-anthropic:
	@echo "🔄 Uploading documents to Anthropic..."
	@if [ ! -d "vector_store_docs" ]; then \
		echo "❌ vector_store_docs/ directory not found. Create vector_store_docs/ and add your knowledge files."; \
		exit 1; \
	fi
	@cd openai_store && python3 anthropic_file_upload.py --dir ../vector_store_docs
	@echo "✅ Documents uploaded to Anthropic"

# Vector Store: Upload to all available providers
vector-upload-all: vector-upload-openai vector-upload-anthropic
	@echo "🎉 Documents uploaded to all available providers!"

# Vector Store: Show status and files
vector-status:
	@echo "📊 Vector Store Status..."
	@echo ""
	@echo "🗂️ Local vector_store_docs directory:"
	@if [ -d "vector_store_docs" ]; then \
		find vector_store_docs -type f -name "*.md" -o -name "*.txt" -o -name "*.pdf" | head -10; \
		echo ""; \
		echo "📋 Total files: $$(find vector_store_docs -type f -name "*.md" -o -name "*.txt" -o -name "*.pdf" | wc -l)"; \
	else \
		echo "❌ vector_store_docs/ directory not found"; \
	fi
	@echo ""
	@echo "🤖 OpenAI Vector Store:"
	@if [ -f "openai_store/openai_vector_store.json" ]; then \
		cat openai_store/openai_vector_store.json | python3 -m json.tool; \
	else \
		echo "❌ No OpenAI vector store manifest found"; \
	fi
	@echo ""
	@echo "🧠 Anthropic Uploads:"
	@if [ -f "openai_store/anthropic_uploads.json" ]; then \
		cat openai_store/anthropic_uploads.json | python3 -m json.tool; \
	else \
		echo "❌ No Anthropic uploads manifest found"; \
	fi

# Vector Store: Test vector store functionality
test-vector-stores:
	@echo "🧪 Testing vector store functionality..."
	python3 tests/test_vector_stores.py

# Vector Store: Integration test (requires API keys)
test-vector-integration:
	@echo "🧪 Running vector store integration test..."
	python3 tests/test_vector_store_integration.py 

# Docker publishing commands
# You can override the Docker Hub username/org with: make docker-push DOCKER_USER=yourusername
DOCKER_USER ?= braincargo
IMAGE_NAME ?= brain-blog
FULL_IMAGE_NAME = $(DOCKER_USER)/$(IMAGE_NAME)

docker-publish:
	@echo "🐳 Building and pushing Docker image to Docker Hub..."
	@echo "📋 Image: $(FULL_IMAGE_NAME):latest"
	docker build -t $(FULL_IMAGE_NAME):latest .
	docker push $(FULL_IMAGE_NAME):latest
	@echo "✅ Docker image pushed to $(FULL_IMAGE_NAME):latest"

docker-push: docker-publish

docker-tag:
	@echo "🏷️ Tagging Docker image with version..."
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Please specify VERSION=x.x.x"; \
		echo "Example: make docker-tag VERSION=1.0.0"; \
		echo "Optional: make docker-tag VERSION=1.0.0 DOCKER_USER=yourusername"; \
		exit 1; \
	fi
	@echo "📋 Image: $(FULL_IMAGE_NAME):$(VERSION)"
	docker build -t $(FULL_IMAGE_NAME):latest .
	docker tag $(FULL_IMAGE_NAME):latest $(FULL_IMAGE_NAME):$(VERSION)
	@echo "✅ Tagged as $(FULL_IMAGE_NAME):$(VERSION)"

docker-release:
	@echo "🚀 Building and pushing versioned Docker release..."
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Please specify VERSION=x.x.x"; \
		echo "Example: make docker-release VERSION=1.0.0"; \
		echo "Optional: make docker-release VERSION=1.0.0 DOCKER_USER=yourusername"; \
		exit 1; \
	fi
	@echo "📋 Image: $(FULL_IMAGE_NAME):$(VERSION)"
	docker build -t $(FULL_IMAGE_NAME):latest .
	docker tag $(FULL_IMAGE_NAME):latest $(FULL_IMAGE_NAME):$(VERSION)
	docker push $(FULL_IMAGE_NAME):latest
	docker push $(FULL_IMAGE_NAME):$(VERSION)
	@echo "🎉 Released $(FULL_IMAGE_NAME):$(VERSION) and $(FULL_IMAGE_NAME):latest"

docker-test:
	@echo "🧪 Testing Docker image..."
	@echo "📋 Testing: $(FULL_IMAGE_NAME):latest"
	docker run --rm -p 8081:8080 -d --name braincargo-test $(FULL_IMAGE_NAME):latest
	@sleep 10
	@echo "Testing health endpoint..."
	@curl -f http://localhost:8081/health || (docker stop braincargo-test && exit 1)
	@docker stop braincargo-test
	@echo "✅ Docker image test passed"

prepare-distribution:
	@echo "📦 Preparing distribution package..."
	@./scripts/prepare-distribution.sh $(VERSION) 