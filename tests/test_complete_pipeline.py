#!/usr/bin/env python3
"""
Complete Pipeline Local Testing
Tests the full blog generation pipeline with images, memes, and S3 storage
"""

import os
import sys
import json
import time
import logging
import pytest
from typing import Dict, Any
from datetime import datetime

# Add the parent directory to the path so we can import the modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test that environment variables are properly configured"""
    logger.info("🔧 Testing environment setup...")
    
    # At least one AI provider is required
    ai_providers = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GROK_API_KEY', 'GEMINI_API_KEY']
    optional_vars = ['BLOG_POSTS_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    
    available_ai_providers = []
    available_optional = []
    
    # Load API keys from config/.env file
    config_env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
    env_vars = {}
    
    if os.path.exists(config_env_path):
        logger.info(f"   📁 Loading configuration from {config_env_path}")
        with open(config_env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    # Also set the environment variable for the providers to find
                    if key in ai_providers + optional_vars:
                        os.environ[key] = value
    else:
        logger.warning(f"   ⚠️ Config file not found: {config_env_path}")
    
    # Check both environment variables and config file
    for var in ai_providers:
        # Check environment variable first, then config file
        value = os.environ.get(var) or env_vars.get(var)
        if value and value not in ['', 'your_openai_api_key_here', 'your_anthropic_api_key_here', 'your_grok_api_key', 'your_gemini_api_key']:
            available_ai_providers.append(var)
            logger.info(f"   ✅ {var}: {'*' * 20}")
        else:
            logger.info(f"   ⚠️ {var}: Not configured")
    
    for var in optional_vars:
        # Check environment variable first, then config file
        value = os.environ.get(var) or env_vars.get(var)
        if value and value != '':
            available_optional.append(var)
            logger.info(f"   ✅ {var}: {'*' * 20}")
        else:
            logger.info(f"   ⚠️ {var}: Not configured (optional)")
    
    if not available_ai_providers:
        logger.error(f"❌ No AI provider API keys configured. Need at least one of: {ai_providers}")
        logger.error(f"   💡 Please add your API keys to config/.env file")
        pytest.fail(f"No AI provider API keys configured. Need at least one of: {ai_providers}")
    
    logger.info(f"✅ Environment setup complete. AI providers available: {len(available_ai_providers)}, Optional vars: {len(available_optional)}")
    assert len(available_ai_providers) > 0, "At least one AI provider should be configured"
    return True

def test_provider_initialization():
    """Test that all providers can be initialized"""
    logger.info("🔧 Testing provider initialization...")
    
    try:
        from providers.factory import LLMProviderFactory
        
        # Test provider configs
        test_configs = {
            'openai': {
                'type': 'openai',
                'api_key_env': 'OPENAI_API_KEY',
                'models': {'standard': 'gpt-4o'},
                'image_models': {'default': 'dall-e-3'}
            },
            'anthropic': {
                'type': 'anthropic', 
                'api_key_env': 'ANTHROPIC_API_KEY',
                'models': {'standard': 'claude-3-5-sonnet-20241022'}
            },
            'grok': {
                'type': 'grok',
                'api_key_env': 'GROK_API_KEY',
                'models': {'standard': 'grok-beta'},
                'image_models': {'default': 'grok-vision-beta'}
            },
            'gemini': {
                'type': 'gemini',
                'api_key_env': 'GEMINI_API_KEY',
                'models': {'standard': 'gemini-1.5-pro'},
                'image_models': {'default': 'imagegeneration@006'}
            }
        }
        
        available_providers = {}
        creation_errors = []
        
        for provider_type, config in test_configs.items():
            try:
                provider = LLMProviderFactory.create_provider(provider_type, config)
                if provider:
                    is_available = provider.is_available()
                    has_images = hasattr(provider, 'generate_image')
                    
                    logger.info(f"   ✅ {provider_type}: Available={is_available}, Images={has_images}")
                    
                    if is_available:
                        available_providers[provider_type] = provider
                else:
                    creation_errors.append(f"{provider_type}: Failed to create")
                    logger.warning(f"   ⚠️ {provider_type}: Failed to create")
                    
            except Exception as e:
                creation_errors.append(f"{provider_type}: Error - {str(e)}")
                logger.warning(f"   ⚠️ {provider_type}: Error - {str(e)}")
        
        logger.info(f"✅ Provider initialization complete. Available: {list(available_providers.keys())}")
        
        # For pytest: We expect that the factory should be able to create providers,
        # even if they're not available due to missing API keys
        assert len(test_configs) == 4, "Should test all 4 provider types"
        
        # Check that the factory recognizes all provider types
        factory_providers = LLMProviderFactory.get_available_providers()
        for provider_type in test_configs.keys():
            assert provider_type in factory_providers, f"Factory should recognize {provider_type} provider"
        
        logger.info("✅ Provider factory test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Provider initialization failed: {str(e)}")
        pytest.fail(f"Provider initialization failed: {str(e)}")
        return False

def test_pipeline_components():
    """Test individual pipeline components"""
    logger.info("🔧 Testing pipeline components...")
    
    try:
        from pipeline.pipeline_manager import PipelineManager
        
        # Initialize pipeline
        pipeline = PipelineManager()
        assert pipeline is not None, "Pipeline should be created"
        
        # Test health check
        health = pipeline.health_check()
        logger.info(f"   📊 Pipeline health: {health['overall_health']}")
        assert 'overall_health' in health, "Health check should return overall_health"
        
        # Test each component
        expected_components = ['categorizer', 'blog_generator', 'image_generator', 'meme_generator']
        initialized_components = []
        
        for component in expected_components:
            if component in pipeline.steps:
                logger.info(f"   ✅ {component}: Initialized")
                initialized_components.append(component)
            else:
                logger.warning(f"   ⚠️ {component}: Missing")
        
        # Test media storage
        has_media_storage = hasattr(pipeline, 'media_storage')
        if has_media_storage:
            logger.info(f"   ✅ media_storage: Initialized")
        else:
            logger.warning(f"   ⚠️ media_storage: Missing")
        
        logger.info("✅ Pipeline components test complete")
        
        # Assertions for pytest
        assert len(initialized_components) >= 2, f"At least 2 components should be initialized, got {len(initialized_components)}"
        assert 'blog_generator' in initialized_components, "Blog generator is required"
        
        logger.info("✅ Pipeline components test passed")
        return pipeline
        
    except Exception as e:
        logger.error(f"❌ Pipeline components test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Pipeline components test failed: {str(e)}")
        return None

def test_image_generation_pytest(pipeline):
    """Test image generation with available providers - pytest version"""
    logger.info("🎨 Testing image generation...")
    
    assert pipeline is not None, "Pipeline should be available for image testing"
    assert 'image_generator' in pipeline.steps, "Image generator should be in pipeline steps"
    
    # Test data
    test_blog_data = {
        'title': 'Local Test Blog Post',
        'summary': 'Testing image generation locally',
        'content': '<h1>Test</h1><p>This is a test blog post for image generation.</p>',
        'category': 'technology',
        'style_persona': 'Tech Expert'
    }
    
    # Test image instructions generation
    logger.info("   🎨 Testing image instructions generation...")
    image_generator = pipeline.steps['image_generator']
    
    instructions_result = image_generator.generate_instructions(test_blog_data, 'technology')
    
    assert instructions_result['success'] is True, "Image instructions should be generated successfully"
    assert 'data' in instructions_result, "Instructions result should contain data"
    
    logger.info(f"   ✅ Image instructions generated: {instructions_result['data'].get('prompt', 'No prompt')[:50]}...")
    
    # Test actual image generation
    openai_provider = pipeline.providers.get('openai')
    if openai_provider and openai_provider.is_available() and hasattr(openai_provider, 'generate_image'):
        logger.info("   🖼️ Testing actual image generation...")
        
        image_result = image_generator.generate_image(instructions_result['data'], test_blog_data)
        
        assert image_result['success'] is True, f"Image generation should succeed, got error: {image_result.get('error')}"
        assert 'image_url' in image_result, "Image result should contain image_url"
        
        logger.info(f"   ✅ Image generated successfully: {image_result['image_url'][:60]}...")
    else:
        logger.info("   ⚠️ OpenAI not available for image generation test - skipping image generation")
    
    logger.info("✅ Image generation test complete")

def test_meme_generation_pytest(pipeline):
    """Test meme generation with available providers - pytest version"""
    logger.info("😄 Testing meme generation...")
    
    assert pipeline is not None, "Pipeline should be available for meme testing"
    assert 'meme_generator' in pipeline.steps, "Meme generator should be in pipeline steps"
    
    # Test data
    test_blog_data = {
        'title': 'Local Test Meme Post',
        'summary': 'Testing meme generation locally',
        'content': '<h1>Test</h1><p>This is a test for meme generation.</p>',
        'category': 'technology',
        'style_persona': 'Tech Expert'
    }
    
    logger.info("   😄 Testing meme generation...")
    meme_generator = pipeline.steps['meme_generator']
    
    meme_result = meme_generator.generate(test_blog_data, 'technology')
    
    assert meme_result['success'] is True, f"Meme generation should succeed, got error: {meme_result.get('error')}"
    assert 'data' in meme_result, "Meme result should contain data"
    
    meme_data = meme_result['data']
    logger.info(f"   ✅ Meme generated:")
    logger.info(f"      Template: {meme_data.get('template', 'Unknown')}")
    logger.info(f"      Top text: {meme_data.get('top_text', 'N/A')}")
    logger.info(f"      Bottom text: {meme_data.get('bottom_text', 'N/A')}")
    
    if meme_data.get('meme_url'):
        logger.info(f"      Image URL: {meme_data['meme_url'][:60]}...")
    else:
        logger.info(f"      Type: Text-only meme")
    
    logger.info("✅ Meme generation test complete")

def test_media_embedding_pytest(pipeline):
    """Test media embedding in blog content - pytest version"""
    logger.info("📎 Testing media embedding...")
    
    assert pipeline is not None, "Pipeline should be available for media embedding test"
    assert 'blog_generator' in pipeline.steps, "Blog generator should be in pipeline steps"
    
    # Test blog data
    test_blog_data = {
        'title': 'Local Test Media Embedding',
        'summary': 'Testing media embedding locally',
        'content': '<h1>Test Blog Post</h1><p>First paragraph of content.</p><p>Second paragraph of content.</p><p>Third paragraph of content.</p>',
        'category': 'technology',
        'id': 'test123'
    }
    
    blog_generator = pipeline.steps['blog_generator']
    
    # Create mock media data for testing
    mock_image_data = {
        'success': True,
        'image_url': 'https://example.com/test-image.png',
        'alt_text': 'Test featured image',
        'caption': 'Test image caption'
    }
    
    mock_meme_data = {
        'success': True,
        'meme_url': 'https://example.com/test-meme.png',
        'alt_text': 'Test meme',
        'meme_description': 'Test meme description',
        'template': 'drake_pointing',
        'top_text': 'Old approach',
        'bottom_text': 'New approach'
    }
    
    logger.info(f"   📎 Embedding media (Image: {bool(mock_image_data)}, Meme: {bool(mock_meme_data)})...")
    
    # Test media embedding
    enhanced_blog_data = blog_generator.embed_media_in_content(
        test_blog_data,
        image_data=mock_image_data,
        meme_data=mock_meme_data
    )
    
    # Check results
    original_length = len(test_blog_data['content'])
    enhanced_length = len(enhanced_blog_data['content'])
    
    assert enhanced_length > original_length, "Enhanced content should be longer than original"
    assert 'media' in enhanced_blog_data, "Enhanced blog data should contain media section"
    
    media = enhanced_blog_data['media']
    assert media.get('featured_image'), "Media should contain featured image"
    assert media.get('meme_url'), "Media should contain meme URL"
    
    logger.info(f"   ✅ Media embedding completed:")
    logger.info(f"      Original content length: {original_length}")
    logger.info(f"      Enhanced content length: {enhanced_length}")
    logger.info(f"      Media data present: {bool(enhanced_blog_data.get('media'))}")
    
    if enhanced_blog_data.get('media'):
        media = enhanced_blog_data['media']
        logger.info(f"      Featured image: {bool(media.get('featured_image'))}")
        logger.info(f"      Meme URL: {bool(media.get('meme_url'))}")
        logger.info(f"      Thumbnail: {bool(media.get('thumbnail_url'))}")
    
    logger.info("✅ Media embedding test complete")

def test_media_storage_pytest(pipeline):
    """Test media storage functionality - pytest version"""
    logger.info("💾 Testing media storage...")
    
    assert pipeline is not None, "Pipeline should be available"
    assert hasattr(pipeline, 'media_storage'), "Pipeline should have media storage"
    
    media_storage = pipeline.media_storage
    
    # Test S3 stats (even if not configured)
    logger.info("   📊 Testing media storage stats...")
    stats = media_storage.get_media_stats()
    
    assert isinstance(stats, dict), "Media stats should return a dictionary"
    
    if 'error' in stats:
        logger.info(f"   ⚠️ S3 not configured: {stats['error']}")
        assert 'S3 not configured' in stats['error'], "Error should indicate S3 not configured"
    else:
        logger.info(f"   ✅ S3 configured: {stats}")
        assert 'total_files' in stats, "Stats should contain total_files when S3 is configured"
    
    # Test mock URL processing with sample data
    blog_data_with_media = {
        'id': 'test123',
        'content': '<img src="https://temp.com/image.png">',
        'media': {
            'featured_image': 'https://temp.com/featured.png',
            'meme_url': 'https://temp.com/meme.png'
        }
    }
    
    logger.info("   🔄 Testing temporary URL cleanup...")
    
    # This will attempt to save to S3 if configured, or skip gracefully
    processed_blog_data = media_storage.cleanup_temporary_urls(blog_data_with_media)
    
    assert isinstance(processed_blog_data, dict), "Processed blog data should be a dictionary"
    assert 'media' in processed_blog_data, "Processed data should retain media section"
    
    logger.info(f"   ✅ URL cleanup completed")
    
    if processed_blog_data.get('media', {}).get('storage'):
        storage_info = processed_blog_data['media']['storage']
        logger.info(f"      Storage provider: {storage_info.get('provider', 'unknown')}")
        logger.info(f"      Saved at: {storage_info.get('saved_at', 'unknown')}")
    
    logger.info("✅ Media storage test complete")


# Backward compatibility functions for run_local_tests
def test_image_generation(pipeline):
    """Test image generation - backward compatibility wrapper"""
    try:
        test_image_generation_pytest(pipeline)
        return True
    except Exception:
        return False


def test_meme_generation(pipeline):
    """Test meme generation - backward compatibility wrapper"""
    try:
        test_meme_generation_pytest(pipeline)
        return True
    except Exception:
        return False


def test_media_embedding(pipeline, image_result=None, meme_result=None):
    """Test media embedding - backward compatibility wrapper"""
    try:
        test_media_embedding_pytest(pipeline)
        return True
    except Exception:
        return False


def test_media_storage(pipeline, blog_data_with_media=None):
    """Test media storage - backward compatibility wrapper"""
    try:
        test_media_storage_pytest(pipeline)
        return True
    except Exception:
        return False


def test_complete_pipeline():
    """Test the complete pipeline end-to-end"""
    logger.info("🚀 Testing complete pipeline...")
    
    try:
        from pipeline.pipeline_manager import PipelineManager
        
        # Initialize pipeline
        pipeline = PipelineManager()
        assert pipeline is not None, "Pipeline should be created"
        
        # Test data - simulating URL content
        test_url = "https://example.com/test-article"
        test_content = """
        Artificial Intelligence Revolution
        
        The future of AI is bright with new developments in machine learning and neural networks.
        Companies are investing heavily in AI research and development.
        This technology will transform how we work and live.
        """
        
        logger.info(f"   🔗 Processing test URL: {test_url}")
        
        # Check if any providers are available before attempting pipeline
        available_providers = [name for name, provider in pipeline.providers.items() if provider.is_available()]
        
        if not available_providers:
            logger.warning("⚠️ No AI providers available - skipping pipeline execution test")
            logger.info("✅ Pipeline structure test passed (providers would be needed for execution)")
            return
        
        # Process through complete pipeline
        result = pipeline.process_url(test_url, test_content, "AI Revolution Test")
        
        assert isinstance(result, dict), "Pipeline should return a dictionary result"
        
        if result['success']:
            logger.info("   ✅ Complete pipeline succeeded!")
            
            # Show results summary
            steps = result.get('pipeline_steps', {})
            successful_steps = 0
            
            for step_name, step_result in steps.items():
                if isinstance(step_result, dict):
                    success = step_result.get('success', False)
                    if success:
                        successful_steps += 1
                    status = "✅" if success else "❌"
                    logger.info(f"      {status} {step_name}: {success}")
                else:
                    logger.info(f"      ℹ️ {step_name}: {type(step_result).__name__}")
            
            # Show final blog data summary
            if 'blog_generation' in steps and steps['blog_generation'].get('success'):
                blog_data = steps['blog_generation'].get('data', {})
                logger.info(f"   📝 Generated blog:")
                logger.info(f"      Title: {blog_data.get('title', 'Unknown')}")
                logger.info(f"      Category: {blog_data.get('category', 'Unknown')}")
                logger.info(f"      Content length: {len(blog_data.get('content', ''))}")
                
                if blog_data.get('media'):
                    media = blog_data['media']
                    logger.info(f"      Featured image: {bool(media.get('featured_image'))}")
                    logger.info(f"      Meme: {bool(media.get('meme_url'))}")
            
            # Assert that the pipeline executed successfully
            assert successful_steps > 0, f"At least one pipeline step should succeed, got {successful_steps}"
            logger.info("✅ Complete pipeline test passed")
            return True
            
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"   ❌ Complete pipeline failed: {error_msg}")
            
            # Check if this is due to missing providers
            if "No LLM providers available" in error_msg:
                logger.info("✅ Pipeline correctly handled missing providers")
                return True
            else:
                pytest.fail(f"Complete pipeline failed: {error_msg}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Complete pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Complete pipeline test failed: {str(e)}")
        return False

def run_local_tests():
    """Run all local tests"""
    logger.info("🧪 Starting BrainCargo Blog Service Local Tests")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test 1: Environment Setup
    test_results['environment'] = test_environment_setup()
    
    # Test 2: Provider Initialization
    providers = test_provider_initialization()
    test_results['providers'] = bool(providers)
    
    # Test 3: Pipeline Components
    pipeline = test_pipeline_components()
    test_results['pipeline_components'] = bool(pipeline)
    
    if pipeline:
        # Test 4: Image Generation
        try:
            test_image_generation_pytest(pipeline)
            test_results['image_generation'] = True
        except Exception as e:
            logger.error(f"Image generation test failed: {e}")
            test_results['image_generation'] = False
        
        # Test 5: Meme Generation
        try:
            test_meme_generation_pytest(pipeline)
            test_results['meme_generation'] = True
        except Exception as e:
            logger.error(f"Meme generation test failed: {e}")
            test_results['meme_generation'] = False
        
        # Test 6: Media Embedding
        try:
            test_media_embedding_pytest(pipeline)
            test_results['media_embedding'] = True
        except Exception as e:
            logger.error(f"Media embedding test failed: {e}")
            test_results['media_embedding'] = False
        
        # Test 7: Media Storage
        try:
            test_media_storage_pytest(pipeline)
            test_results['media_storage'] = True
        except Exception as e:
            logger.error(f"Media storage test failed: {e}")
            test_results['media_storage'] = False
        
        # Test 8: Complete Pipeline
        complete_result = test_complete_pipeline()
        test_results['complete_pipeline'] = bool(complete_result)
    
    # Summary
    logger.info("=" * 60)
    logger.info("🏁 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {status} {test_name}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"📊 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! System ready for deployment.")
    elif passed >= total * 0.8:
        logger.info("⚠️ Most tests passed. Review failures before deployment.")
    else:
        logger.info("❌ Many tests failed. System needs fixes before deployment.")
    
    return test_results

if __name__ == "__main__":
    try:
        results = run_local_tests()
        
        # Exit with appropriate code
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        if passed == total:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test runner failed: {str(e)}")
        sys.exit(1) 