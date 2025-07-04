"""
Pipeline Manager - Orchestrates the entire blog generation pipeline
"""

import logging
import yaml
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from .categorizer import URLCategorizer
from .blog_generator import BlogGenerator
from .image_generator import ImageGenerator
from .meme_generator import MemeGenerator
from .media_storage import MediaStorageManager
from providers import LLMProviderFactory

logger = logging.getLogger(__name__)


class PipelineManager:
    """Manages the entire blog generation pipeline"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the pipeline manager
        
        Args:
            config_path: Path to the pipeline configuration YAML file
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'config', 'pipeline.yaml')
        self.config = self._load_config()
        self.providers = {}
        self.steps = {}
        
        # Detect test mode
        self.test_mode = self._is_test_mode()
        if self.test_mode:
            logger.info("🚀 TEST MODE ENABLED - Using fast, cheap models for testing")
        
        # Initialize providers and steps
        self._initialize_providers()
        self._initialize_steps()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
                # Expand environment variables in config
                config = self._expand_env_variables(config)
                
                logger.info(f"✅ Loaded pipeline configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {str(e)}")
            raise
    
    def _expand_env_variables(self, obj):
        """Recursively expand environment variables in configuration"""
        if isinstance(obj, dict):
            return {k: self._expand_env_variables(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_variables(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.environ.get(env_var, obj)
        else:
            return obj
    
    def _is_test_mode(self) -> bool:
        """Check if test mode is enabled"""
        # Check environment variable first
        env_test_mode = os.environ.get('ENABLE_TEST_MODE', '').lower()
        if env_test_mode in ('true', '1', 'yes', 'on'):
            return True
        
        # Check config file
        config_test_mode = self.config.get('environment', {}).get('test_mode', '').lower()
        if config_test_mode in ('true', '1', 'yes', 'on'):
            return True
            
        return False
    
    def _initialize_providers(self):
        """Initialize all LLM providers"""
        provider_configs = self.config.get('providers', {})
        
        # Switch to test models if test mode is enabled
        if self.test_mode:
            provider_configs = self._apply_test_mode_to_providers(provider_configs)
        
        # Use create_multiple_providers instead of get_available_providers
        self.providers = LLMProviderFactory.create_multiple_providers(provider_configs)
        
        if not self.providers:
            logger.error("❌ No LLM providers available")
            raise Exception("No LLM providers available")
        
        mode_info = " (TEST MODE)" if self.test_mode else ""
        logger.info(f"✅ Initialized providers{mode_info}: {list(self.providers.keys())}")
    
    def _apply_test_mode_to_providers(self, provider_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply test mode configuration to providers"""
        updated_configs = {}
        
        for provider_name, config in provider_configs.items():
            updated_config = config.copy()
            
            # If test_models are defined, use them
            if 'test_models' in config:
                logger.info(f"🧪 Switching {provider_name} to test models")
                updated_config['models'] = config['test_models']
            
            updated_configs[provider_name] = updated_config
        
        return updated_configs
    
    def _initialize_steps(self):
        """Initialize all pipeline steps"""
        try:
            self.steps = {
                'categorizer': URLCategorizer(self.config, self.providers),
                'blog_generator': BlogGenerator(self.config, self.providers),
                'image_generator': ImageGenerator(self.config, self.providers),
                'meme_generator': MemeGenerator(self.config, self.providers)
            }
            
            # Initialize media storage manager
            self.media_storage = MediaStorageManager(self.config)
            
            logger.info("✅ Initialized all pipeline steps and media storage")
        except Exception as e:
            logger.error(f"❌ Failed to initialize pipeline steps: {str(e)}")
            raise
    
    def process_url(self, url: str, content: str, custom_title: str = "") -> Dict[str, Any]:
        """
        Process a URL through the complete pipeline
        
        Args:
            url: Source URL
            content: Extracted content from URL
            custom_title: Optional custom title
            
        Returns:
            Complete pipeline results
        """
        logger.info(f"🚀 Starting pipeline for URL: {url}")
        
        results = {
            'url': url,
            'custom_title': custom_title,
            'pipeline_steps': {},
            'success': False,
            'error': None
        }
        
        try:
            # Step 1: Categorize the content
            import time
            step_start = time.time()
            logger.info("📋 Step 1: Categorizing content...")
            categorization = self.steps['categorizer'].categorize(url, content)
            step_duration = time.time() - step_start
            logger.info(f"📋 Step 1 completed in {step_duration:.2f} seconds")
            results['pipeline_steps']['categorization'] = categorization
            
            if not categorization['success']:
                raise Exception(f"Categorization failed: {categorization.get('error')}")
            
            category = categorization['category']
            logger.info(f"✅ Content categorized as: {category}")
            
            # Step 2: Generate blog post
            step_start = time.time()
            logger.info("📝 Step 2: Generating blog post...")
            blog_post = self.steps['blog_generator'].generate(
                url=url,
                content=content,
                category=category,
                custom_title=custom_title,
                categorization_data=categorization
            )
            step_duration = time.time() - step_start
            logger.info(f"📝 Step 2 completed in {step_duration:.2f} seconds")
            results['pipeline_steps']['blog_generation'] = blog_post
            
            if not blog_post['success']:
                raise Exception(f"Blog generation failed: {blog_post.get('error')}")
            
            logger.info(f"✅ Blog post generated: {blog_post['data']['title']}")
            
            # Step 3: Generate image instructions and actual image (if enabled)
            featured_image_data = None
            if self.config.get('image_generation', {}).get('enabled', True):
                logger.info("🎨 Step 3: Generating image instructions...")
                image_instructions = self.steps['image_generator'].generate_instructions(
                    blog_post=blog_post['data'],
                    category=category
                )
                results['pipeline_steps']['image_instructions'] = image_instructions
                
                if image_instructions['success']:
                    logger.info("✅ Image instructions generated")
                    
                    # Generate the actual image
                    logger.info("🖼️ Step 3b: Creating featured image...")
                    try:
                        featured_image_data = self.steps['image_generator'].generate_image(
                            image_instructions['data'],
                            blog_post['data'],
                            category
                        )
                        results['pipeline_steps']['featured_image'] = featured_image_data
                        
                        if featured_image_data['success']:
                            logger.info("✅ Featured image created successfully")
                        else:
                            logger.warning(f"⚠️ Featured image creation failed: {featured_image_data.get('error')}")
                    except Exception as e:
                        logger.error(f"❌ Featured image creation error: {str(e)}")
                        featured_image_data = {'success': False, 'error': str(e)}
                        results['pipeline_steps']['featured_image'] = featured_image_data
                else:
                    logger.warning(f"⚠️ Image instructions failed: {image_instructions.get('error')}")
            
            # Step 4: Generate meme (if enabled)
            meme_data = None
            if self.config.get('meme_generation', {}).get('enabled', True):
                logger.info("😄 Step 4: Generating meme...")
                meme_data = self.steps['meme_generator'].generate(
                    blog_post=blog_post['data'],
                    category=category
                )
                results['pipeline_steps']['meme_generation'] = meme_data
                
                if meme_data['success']:
                    logger.info("✅ Meme generated")
                else:
                    logger.warning(f"⚠️ Meme generation failed: {meme_data.get('error')}")
            
            # Step 5: Embed media into blog content
            enhanced_blog_data = blog_post['data']
            if featured_image_data or meme_data:
                logger.info("📎 Step 5: Embedding media in blog content...")
                try:
                    enhanced_blog_data = self.steps['blog_generator'].embed_media_in_content(
                        blog_post['data'],
                        image_data=featured_image_data if featured_image_data and featured_image_data.get('success') else None,
                        meme_data=meme_data.get('data') if meme_data and meme_data.get('success') else None
                    )
                    logger.info("✅ Media embedded in blog content")
                    results['pipeline_steps']['media_embedding'] = {'success': True}
                except Exception as e:
                    logger.error(f"❌ Media embedding failed: {str(e)}")
                    results['pipeline_steps']['media_embedding'] = {'success': False, 'error': str(e)}
            
            # Step 6: Save media to S3 and replace temporary URLs
            if enhanced_blog_data.get('media'):
                logger.info("💾 Step 6: Saving media to S3...")
                try:
                    enhanced_blog_data = self.media_storage.cleanup_temporary_urls(enhanced_blog_data)
                    logger.info("✅ Media saved to S3 with permanent URLs")
                    results['pipeline_steps']['media_storage'] = {'success': True}
                except Exception as e:
                    logger.error(f"❌ Media storage failed: {str(e)}")
                    results['pipeline_steps']['media_storage'] = {'success': False, 'error': str(e)}
            
            # Update the final blog post data
            results['pipeline_steps']['blog_generation']['data'] = enhanced_blog_data
            
            # Mark pipeline as successful
            results['success'] = True
            logger.info("🎉 Pipeline completed successfully with permanent media storage!")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Pipeline failed: {error_msg}")
            results['error'] = error_msg
            results['success'] = False
        
        return results
    
    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pipeline step"""
        pipeline_steps = self.config.get('pipeline', {}).get('steps', [])
        for step in pipeline_steps:
            if step.get('name') == step_name:
                return step
        return {}
    
    def get_category_config(self, category: str) -> Dict[str, Any]:
        """Get configuration for a specific category"""
        categories = self.config.get('categories', {})
        return categories.get(category, {})
    
    def get_provider(self, provider_name: str) -> Optional[Any]:
        """Get a specific provider instance"""
        return self.providers.get(provider_name)
    
    def reload_config(self):
        """Reload configuration and reinitialize components"""
        logger.info("🔄 Reloading pipeline configuration...")
        try:
            self.config = self._load_config()
            self._initialize_providers()
            self._initialize_steps()
            logger.info("✅ Configuration reloaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to reload configuration: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all pipeline components"""
        health = {
            'pipeline_manager': True,
            'config_loaded': bool(self.config),
            'providers': {},
            'steps': {},
            'overall_health': True
        }
        
        # Check providers
        for name, provider in self.providers.items():
            is_available = provider.is_available()
            health['providers'][name] = is_available
            if not is_available:
                health['overall_health'] = False
        
        # Check steps
        for name, step in self.steps.items():
            try:
                # Basic health check for each step
                health['steps'][name] = True
            except Exception:
                health['steps'][name] = False
                health['overall_health'] = False
        
        return health

    def process_topic(self, topic: str, provider: str = None, style: str = None) -> Dict[str, Any]:
        """
        Process a topic through blog generation
        
        Args:
            topic: Topic to write about
            provider: Optional specific provider to use
            style: Optional style override
            
        Returns:
            Blog generation results
        """
        logger.info(f"🚀 Starting topic processing: {topic}")
        
        results = {
            'topic': topic,
            'provider': provider,
            'style': style,
            'success': False,
            'error': None
        }
        
        try:
            # Create synthetic content from topic
            content = f"Topic: {topic}\n\nThis is a blog post about {topic}. Please generate comprehensive content covering this topic."
            
            # Use the blog generator directly for topic-based generation
            blog_generator = self.steps['blog_generator']
            category = style or 'technology'  # Default category
            
            # Generate blog post
            blog_result = blog_generator.generate(
                url="",
                content=content,
                category=category,
                custom_title="",
                categorization_data={'category': category, 'success': True}
            )
            
            if not blog_result['success']:
                raise Exception(f"Blog generation failed: {blog_result.get('error')}")
            
            # Add metadata
            blog_data = blog_result['data']
            blog_data.update({
                'id': blog_data.get('id', str(__import__('uuid').uuid4())[:8]),
                'source_type': 'topic',
                'source_topic': topic,
                'generated_at': blog_data.get('generated_at', __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat() + 'Z'),
                'word_count': len(blog_data.get('content', '').split()),
                'reading_time': max(1, len(blog_data.get('content', '').split()) // 200),
            })
            
            results['success'] = True
            results['data'] = blog_data
            logger.info(f"✅ Topic processing completed: {blog_data['title']}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Topic processing failed: {error_msg}")
            results['error'] = error_msg
            results['success'] = False
        
        return results
    
    def process_content(self, content: str, title: str = None, provider: str = None) -> Dict[str, Any]:
        """
        Process custom content through blog generation
        
        Args:
            content: Content to transform into blog post
            title: Optional custom title
            provider: Optional specific provider to use
            
        Returns:
            Blog generation results
        """
        logger.info(f"🚀 Starting content processing: {len(content)} characters")
        
        results = {
            'content_length': len(content),
            'custom_title': title,
            'provider': provider,
            'success': False,
            'error': None
        }
        
        try:
            # Use the blog generator directly for content transformation
            blog_generator = self.steps['blog_generator']
            
            # Generate blog post from content
            blog_result = blog_generator.generate(
                url="",
                content=content,
                category='general',
                custom_title=title or "",
                categorization_data={'category': 'general', 'success': True}
            )
            
            if not blog_result['success']:
                raise Exception(f"Blog generation failed: {blog_result.get('error')}")
            
            # Add metadata
            blog_data = blog_result['data']
            blog_data.update({
                'id': blog_data.get('id', str(__import__('uuid').uuid4())[:8]),
                'source_type': 'content',
                'custom_title': title,
                'generated_at': blog_data.get('generated_at', __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat() + 'Z'),
                'word_count': len(blog_data.get('content', '').split()),
                'reading_time': max(1, len(blog_data.get('content', '').split()) // 200),
            })
            
            results['success'] = True
            results['data'] = blog_data
            logger.info(f"✅ Content processing completed: {blog_data['title']}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Content processing failed: {error_msg}")
            results['error'] = error_msg
            results['success'] = False
        
        return results 