"""
Pytest configuration and fixtures for Brain Blog Generator tests.
"""

import pytest
import logging
import os
import sys
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def mock_config():
    """Mock configuration for testing"""
    return {
        'blog': {
            'domain': 'testdomain.com',
            'company_name': 'Test Company',
            'service_name': 'Test Blog Service',
            'call_to_action': 'Test CTA'
        },
        'media': {
            'prefix': 'test-media',
            'cdn_base_url': 'https://test-cdn.com'
        },
        'image_generation': {
            'provider': 'openai',
            'size': '1792x1024',
            'quality': 'hd'
        },
        'meme_generation': {
            'provider': 'openai',
            'templates': ['drake_pointing', 'distracted_boyfriend']
        },
        'error_handling': {
            'retry_attempts': 3
        },
        'categories': {
            'technology': {
                'image_provider': 'openai',
                'meme_provider': 'openai'
            }
        }
    }


@pytest.fixture(scope="session") 
def mock_providers():
    """Mock providers for testing"""
    providers = {}
    
    # Mock OpenAI provider
    openai_provider = Mock()
    openai_provider.is_available.return_value = True
    openai_provider.provider_name = 'openai'
    openai_provider.provider_type = 'openai'
    openai_provider.generate_completion.return_value = {
        'success': True,
        'content': '{"prompt": "test prompt", "style": "modern", "colors": "gold accents"}',
        'model': 'gpt-4'
    }
    openai_provider.generate_image.return_value = {
        'success': True,
        'image_url': 'https://example.com/test-image.png',
        'revised_prompt': 'Enhanced test prompt',
        'model': 'dall-e-3'
    }
    providers['openai'] = openai_provider
    
    # Mock Anthropic provider  
    anthropic_provider = Mock()
    anthropic_provider.is_available.return_value = True
    anthropic_provider.provider_name = 'anthropic'
    anthropic_provider.provider_type = 'anthropic'
    anthropic_provider.generate_completion.return_value = {
        'success': True,
        'content': '{"template": "drake_pointing", "top_text": "Old way", "bottom_text": "New way"}',
        'model': 'claude-3'
    }
    providers['anthropic'] = anthropic_provider
    
    return providers


@pytest.fixture
def pipeline(mock_config, mock_providers):
    """Create a pipeline instance with mocked dependencies"""
    # Mock the YAML file loading and configuration initialization
    with patch('pipeline.pipeline_manager.yaml.safe_load') as mock_yaml_load, \
         patch('builtins.open') as mock_open:
        
        # Mock the config file content
        mock_yaml_load.return_value = mock_config
        mock_open.return_value.__enter__.return_value.read.return_value = "mock config"
        
        # Mock the provider factory
        with patch('pipeline.pipeline_manager.LLMProviderFactory.create_multiple_providers') as mock_factory:
            mock_factory.return_value = mock_providers
            
            from pipeline.pipeline_manager import PipelineManager
            
            # Create pipeline with mocked dependencies
            pipeline_instance = PipelineManager()
            
            # Ensure media storage is initialized
            if not hasattr(pipeline_instance, 'media_storage'):
                from pipeline.media_storage import MediaStorageManager
                pipeline_instance.media_storage = MediaStorageManager(mock_config)
        
            return pipeline_instance


@pytest.fixture
def sample_blog_data():
    """Sample blog data for testing"""
    return {
        'title': 'Test Blog Post: AI Revolution',
        'summary': 'A comprehensive guide to artificial intelligence and machine learning innovations.',
        'content': '<h1>AI Revolution</h1><p>First paragraph about AI.</p><p>Second paragraph about ML.</p><p>Third paragraph about the future.</p>',
        'category': 'technology',
        'style_persona': 'Tech Expert',
        'id': 'test_blog_123'
    }


@pytest.fixture
def sample_image_instructions():
    """Sample image generation instructions"""
    return {
        'prompt': 'Professional technology blog featured image with AI and machine learning themes',
        'style': 'Clean, modern, professional',
        'composition': 'Centered with subtle tech elements',
        'colors': 'Gold accent (#DDBC74) with modern palette',
        'elements': ['neural network', 'circuit patterns', 'gradient background'],
        'mood': 'Innovative and empowering',
        'technical_notes': 'High resolution, 16:9 aspect ratio'
    }


@pytest.fixture
def sample_meme_data():
    """Sample meme data for testing"""
    return {
        'template': 'drake_pointing',
        'top_text': 'Traditional AI',
        'bottom_text': 'Own Your AI',
        'context': 'Comparison meme about AI ownership vs traditional centralized AI',
        'humor_type': 'comparison',
        'relevance': 'Relates to BrainCargo\'s decentralized AI philosophy'
    }


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing media storage"""
    with patch('boto3.client') as mock_boto3:
        mock_client = Mock()
        mock_client.put_object.return_value = {'ETag': 'test-etag'}
        mock_client.list_objects_v2.return_value = {
            'KeyCount': 5,
            'Contents': [
                {'Key': 'media/test1.png', 'Size': 1024},
                {'Key': 'media/test2.png', 'Size': 2048}
            ]
        }
        mock_boto3.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        'BLOG_POSTS_BUCKET': 'test-blog-bucket',
        'MEDIA_PREFIX': 'test-media',
        'CDN_BASE_URL': 'https://test-cdn.com'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env) 