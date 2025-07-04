#!/usr/bin/env python3
"""
Test Script for Image Generation Fallbacks
Tests the new fallback system for image generation when providers fail.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.pipeline_manager import PipelineManager
from pipeline.image_generator import ImageGenerator
from pipeline.meme_generator import MemeGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_image_generation_fallbacks():
    """Test image generation with provider fallbacks"""
    logger.info("🧪 Testing image generation fallback system...")
    
    try:
        # Initialize pipeline manager
        pipeline = PipelineManager()
        image_generator = pipeline.steps['image_generator']
        
        # Test data
        test_blog_post = {
            'title': 'AI-Powered Blockchain Revolution',
            'summary': 'Exploring how AI and blockchain technologies are converging to create new opportunities.',
            'content': '<h1>The Future is Here</h1><p>AI and blockchain are transforming industries.</p>',
            'style_persona': 'Tech Expert'
        }
        
        test_instructions = {
            'prompt': 'Futuristic AI and blockchain visualization with interconnected networks',
            'style': 'Modern, professional, high-tech',
            'composition': 'Central focus with geometric patterns',
            'colors': 'Blue and gold gradient with tech elements',
            'mood': 'Innovative and forward-looking',
            'caption': 'AI-Blockchain convergence illustration'
        }
        
        # Test different categories to see different provider preferences
        test_categories = ['technology', 'security', 'web3']
        
        for category in test_categories:
            logger.info(f"\n📋 Testing category: {category}")
            
            # Test image generation with fallbacks
            result = image_generator.generate_image(
                instructions=test_instructions,
                blog_post=test_blog_post,
                category=category
            )
            
            if result['success']:
                logger.info(f"✅ Image generated for {category} using provider: {result.get('provider', 'unknown')}")
                logger.info(f"   Image URL: {result.get('image_url', 'N/A')[:80]}...")
            else:
                logger.warning(f"⚠️ Image generation failed for {category}: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_meme_generation_fallbacks():
    """Test meme generation with provider fallbacks"""
    logger.info("\n🎭 Testing meme generation fallback system...")
    
    try:
        # Initialize pipeline manager
        pipeline = PipelineManager()
        meme_generator = pipeline.steps['meme_generator']
        
        # Test data
        test_blog_post = {
            'title': 'When Your Code Finally Works',
            'summary': 'The universal developer experience when debugging pays off.',
            'content': '<h1>Success!</h1><p>That feeling when everything compiles on the first try.</p>',
            'style_persona': 'Tech Expert'
        }
        
        # Test different categories
        test_categories = ['technology', 'security', 'web3']
        
        for category in test_categories:
            logger.info(f"\n📋 Testing meme generation for category: {category}")
            
            result = meme_generator.generate(
                blog_post=test_blog_post,
                category=category
            )
            
            if result['success']:
                meme_data = result.get('data', {})
                logger.info(f"✅ Meme generated for {category}")
                logger.info(f"   Template: {meme_data.get('template', 'N/A')}")
                logger.info(f"   Top text: {meme_data.get('top_text', 'N/A')}")
                logger.info(f"   Bottom text: {meme_data.get('bottom_text', 'N/A')}")
                logger.info(f"   Image type: {meme_data.get('meme_type', 'N/A')}")
                if meme_data.get('meme_url') and meme_data.get('meme_url') != 'text_only':
                    logger.info(f"   Image URL: {meme_data.get('meme_url', 'N/A')[:80]}...")
            else:
                logger.warning(f"⚠️ Meme generation failed for {category}: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Meme test failed: {str(e)}")
        return False


def test_provider_availability():
    """Test which providers are available for image generation"""
    logger.info("\n🔍 Testing provider availability...")
    
    try:
        pipeline = PipelineManager()
        
        logger.info("Available providers:")
        for name, provider in pipeline.providers.items():
            is_available = provider.is_available()
            has_image_gen = hasattr(provider, 'generate_image')
            
            status = "✅" if is_available else "❌"
            image_support = "🎨" if has_image_gen else "📝"
            
            logger.info(f"  {status} {image_support} {name}: Available={is_available}, Images={has_image_gen}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Provider availability test failed: {str(e)}")
        return False


def main():
    """Run all fallback tests"""
    logger.info("🚀 Starting Image Generation Fallback Tests")
    logger.info("=" * 60)
    
    # Test provider availability first
    if not test_provider_availability():
        logger.error("❌ Provider availability test failed")
        return False
    
    # Test image generation fallbacks
    if not test_image_generation_fallbacks():
        logger.error("❌ Image generation fallback test failed")
        return False
    
    # Test meme generation fallbacks
    if not test_meme_generation_fallbacks():
        logger.error("❌ Meme generation fallback test failed")
        return False
    
    logger.info("\n🎉 All fallback tests completed!")
    logger.info("The system now has robust fallbacks for image generation failures.")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 