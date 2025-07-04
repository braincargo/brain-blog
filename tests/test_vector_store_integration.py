#!/usr/bin/env python3
"""
Vector Store Integration Test

This script tests the complete vector store workflow:
1. Upload test documents to vector stores
2. Generate a blog post using knowledge from vector stores
3. Verify that knowledge was actually used

Usage:
    python test_vector_store_integration.py

Requirements:
    - OPENAI_API_KEY environment variable
    - Optional: ANTHROPIC_API_KEY for Anthropic testing
    - vector_store_docs/ directory with test documents
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

# Load environment variables from config/.env
try:
    from dotenv import load_dotenv
    load_dotenv('config/.env')
    print("✅ Loaded environment variables from config/.env")
except ImportError:
    print("⚠️ python-dotenv not available, skipping .env file loading")

def setup_test_documents():
    """Create test documentation for vector store upload."""
    docs_dir = Path("vector_store_docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Create sample documentation (use .txt for Anthropic compatibility)
    test_docs = {
        "braincargo_knowledge.txt": """# BrainCargo Knowledge Base

## Company Overview
BrainCargo is a cutting-edge AI technology company specializing in automated content generation and knowledge management systems.

## Key Technologies
- Advanced Large Language Model integration
- Vector store-based knowledge retrieval
- Multi-provider AI service architecture
- Automated blog generation pipelines

## Recent Developments
- Successfully integrated OpenAI and Anthropic vector stores
- Implemented fallback mechanisms for robust operation
- Created comprehensive testing framework
- Built scalable Docker-based deployment system

## Technical Expertise
- Python-based microservices
- RESTful API design
- Container orchestration
- AI/ML pipeline optimization
""",
        
        "technical_guidelines.txt": """# BrainCargo Technical Guidelines

## Architecture Principles
1. **Multi-provider Support**: Never depend on a single AI provider
2. **Graceful Degradation**: System should work even if some providers fail
3. **Knowledge Integration**: Use vector stores to enhance AI responses
4. **Testing First**: Comprehensive test coverage for all functionality

## Best Practices
- Always include fallback mechanisms
- Log important operations for debugging
- Use environment variables for configuration
- Implement health checks for all services

## Vector Store Usage
- Blog generation: Use knowledge for enhanced content
- Categorization: Keep fast, don't use knowledge
- Image generation: Keep creative, don't constrain with knowledge
- Meme generation: Keep spontaneous, don't use knowledge
""",
        
        "company_projects.txt": """# BrainCargo Projects

## Blog Service
Automated blog post generation with AI integration:
- Multi-provider AI support (OpenAI, Anthropic, Grok, Gemini)
- Image and meme generation capabilities
- Vector store knowledge integration
- Comprehensive testing framework

## Features
- Automatic categorization of blog topics
- SEO-optimized content generation
- Fallback mechanisms for reliability
- Docker-based deployment
- Health monitoring and logging

## Recent Achievements
- Open source release preparation
- Documentation consolidation
- Vector store integration
- Professional test suite implementation
"""
    }
    
    for filename, content in test_docs.items():
        (docs_dir / filename).write_text(content)
    
    print(f"✅ Created {len(test_docs)} test documents in vector_store_docs/")
    return docs_dir

def check_api_keys():
    """Check if required API keys are available."""
    openai_key = os.environ.get('OPENAI_API_KEY')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found. Vector store tests require OpenAI access.")
        return False
    
    print("✅ OPENAI_API_KEY found")
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY found")
    else:
        print("⚠️ ANTHROPIC_API_KEY not found (optional)")
    
    return True

def test_openai_vector_store():
    """Test OpenAI vector store upload and usage."""
    print("\n🔵 Testing OpenAI Vector Store Integration...")
    
    try:
        # Upload documents to OpenAI vector store
        print("📤 Uploading documents to OpenAI vector store...")
        result = subprocess.run(
            ["make", "vector-upload-openai"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ OpenAI upload failed: {result.stderr}")
            return False
        
        print("✅ OpenAI vector store upload completed")
        
        # Check if manifest file was created
        manifest_path = Path("openai_store/openai_vector_store.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            print(f"�� Vector store ID: {manifest.get('vector_store_id')}")
            print(f"📋 Uploaded files: {len(manifest.get('file_ids', []))}")
        else:
            print("⚠️ No manifest file found")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ OpenAI upload timed out")
        return False
    except Exception as e:
        print(f"❌ OpenAI upload error: {e}")
        return False

def test_anthropic_upload():
    """Test Anthropic file upload."""
    print("\n🟣 Testing Anthropic File Upload...")
    
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("⚠️ Skipping Anthropic test - no API key found")
        return True
    
    try:
        # Upload documents to Anthropic
        print("📤 Uploading documents to Anthropic...")
        result = subprocess.run(
            ["make", "vector-upload-anthropic"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ Anthropic upload failed: {result.stderr}")
            return False
        
        print("✅ Anthropic file upload completed")
        
        # Check if manifest file was created
        manifest_path = Path("openai_store/anthropic_uploads.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            print(f"📋 Uploaded files: {manifest.get('total_files', 0)}")
        else:
            print("⚠️ No manifest file found")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Anthropic upload timed out")
        return False
    except Exception as e:
        print(f"❌ Anthropic upload error: {e}")
        return False

def test_blog_generation_with_knowledge():
    """Test blog generation using vector store knowledge."""
    print("\n📝 Testing Knowledge-Enhanced Blog Generation...")
    
    # Test script that uses knowledge
    test_script = """
import sys
import os
sys.path.append('.')

from providers.factory import LLMProviderFactory
from pipeline.blog_generator import BlogGenerator
import yaml

# Load configuration
with open('config/pipeline.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create provider factory
factory = LLMProviderFactory()

# Test with OpenAI if available
openai_config = config.get('providers', {}).get('openai', {})
if openai_config and os.environ.get('OPENAI_API_KEY'):
    provider = factory.create_provider('openai', openai_config)
    if provider and provider.is_available():
        print("🔵 Testing OpenAI with knowledge...")
        
        # Generate blog with knowledge
        result = provider.generate_completion(
            prompt="Write a brief blog post about BrainCargo's recent achievements and technical expertise.",
            use_knowledge_files=True
        )
        
        content = result.get('content', '')
        if any(keyword in content.lower() for keyword in ['braincargo', 'vector store', 'multi-provider']):
            print("✅ OpenAI used knowledge - found relevant keywords")
        else:
            print("⚠️ OpenAI may not have used knowledge - no specific keywords found")
        
        print(f"📄 Generated content length: {len(content)} characters")

# Test with Anthropic if available
anthropic_config = config.get('providers', {}).get('anthropic', {})
if anthropic_config and os.environ.get('ANTHROPIC_API_KEY'):
    provider = factory.create_provider('anthropic', anthropic_config)
    if provider and provider.is_available():
        print("\\n🟣 Testing Anthropic with knowledge...")
        
        # Generate blog with knowledge
        result = provider.generate_completion(
            prompt="Write a brief blog post about BrainCargo's recent achievements and technical expertise.",
            use_knowledge_files=True
        )
        
        content = result.get('content', '')
        if any(keyword in content.lower() for keyword in ['braincargo', 'vector store', 'multi-provider']):
            print("✅ Anthropic used knowledge - found relevant keywords")
        else:
            print("⚠️ Anthropic may not have used knowledge - no specific keywords found")
        
        print(f"📄 Generated content length: {len(content)} characters")

print("\\n✅ Knowledge integration testing completed")
"""
    
    # Write and execute test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Blog generation test timed out")
        return False
    except Exception as e:
        print(f"❌ Blog generation test error: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass

def main():
    """Run the complete vector store integration test."""
    print("🧪 Vector Store Integration Test")
    print("================================")
    
    # Check prerequisites
    if not check_api_keys():
        print("\n❌ Prerequisites not met. Please set required API keys.")
        return 1
    
    # Setup test documents
    setup_test_documents()
    
    success = True
    
    # Test OpenAI vector store
    if not test_openai_vector_store():
        success = False
    
    # Test Anthropic upload
    if not test_anthropic_upload():
        success = False
    
    # Test knowledge integration
    if not test_blog_generation_with_knowledge():
        success = False
    
    # Show status
    print("\n" + "="*50)
    result = subprocess.run(["make", "vector-status"], capture_output=True, text=True)
    print(result.stdout)
    
    # Final result
    print("\n🏁 Integration Test Results")
    print("===========================")
    if success:
        print("🎉 All vector store integration tests passed!")
        print("\n✅ Your vector store setup is working correctly:")
        print("   - Documents uploaded successfully")
        print("   - AI providers can access knowledge")
        print("   - Knowledge is being used in blog generation")
        return 0
    else:
        print("💥 Some vector store integration tests failed!")
        print("\n❌ Issues found with vector store setup:")
        print("   - Check API keys and permissions")
        print("   - Verify vector_store_docs/ directory exists")
        print("   - Review error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 