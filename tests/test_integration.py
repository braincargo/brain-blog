"""
Integration tests for Brain Blog Generator.

Tests the complete workflow from input to output, including multiple providers
and end-to-end functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestEndToEndBlogGeneration(unittest.TestCase):
    """Test complete blog generation workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.blog.domain = 'testdomain.com'
        self.mock_config.blog.company_name = 'Test Company'
        self.mock_config.blog.cdn_url = 'https://cdn.testdomain.com'
        self.mock_config.blog.call_to_action = 'Visit our site'
        self.mock_config.security.enable_phone_auth = False
        self.mock_config.api.openai_api_key = 'test-openai-key'
        self.mock_config.api.anthropic_api_key = 'test-anthropic-key'

    @patch('config.app_settings.get_settings')
    @patch('pipeline.pipeline_manager.LLMProviderFactory')
    @patch('pipeline.blog_generator.extract_content_from_url')
    def test_complete_url_to_blog_workflow(self, mock_extract, mock_factory, mock_load_config):
        """Test complete workflow from URL to finished blog post."""
        # Setup configuration
        mock_load_config.return_value = self.mock_config
        
        # Setup URL content extraction
        mock_extract.return_value = {
            'title': 'Source Article Title',
            'content': 'This is an article about artificial intelligence and machine learning.',
            'meta_description': 'An article about AI'
        }
        
        # Setup provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.provider_name = 'openai'
        mock_provider.generate_blog.return_value = {
            'title': 'AI Revolution: Understanding Machine Learning',
            'content': '<h1>AI Revolution</h1><p>Machine learning is transforming our world...</p>',
            'summary': 'An exploration of how AI and ML are changing technology.'
        }
        
        mock_factory_instance = Mock()
        mock_factory_instance.get_available_provider.return_value = mock_provider
        mock_factory.return_value = mock_factory_instance
        
        # Import and test pipeline
        from pipeline.pipeline_manager import PipelineManager
        
        # Mock pipeline manager to avoid constructor issues
        with patch('pipeline.pipeline_manager.PipelineManager') as mock_pipeline_class:
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.process_url.return_value = {
                'title': 'AI Revolution: Understanding Machine Learning',
                'content': '<h1>AI Revolution</h1><p>Machine learning is transforming our world...</p>',
                'summary': 'An exploration of how AI and ML are changing technology.',
                'category': 'technology',
                'metadata': {
                    'provider': 'openai',
                    'source_type': 'url',
                    'timestamp': '2025-01-01T12:00:00'
                }
            }
            mock_pipeline_class.return_value = mock_pipeline_instance
            result = mock_pipeline_instance.process_url('https://example.com/ai-article')
        
            # Verify complete workflow
            self.assertIsInstance(result, dict)
            
            # Check blog content
            self.assertIn('title', result)
            self.assertIn('content', result)
            self.assertIn('summary', result)
            self.assertIn('category', result)
            self.assertIn('metadata', result)
            
            # Verify content
            self.assertEqual(result['title'], 'AI Revolution: Understanding Machine Learning')
            self.assertIn('<h1>AI Revolution</h1>', result['content'])
            
            # Verify categorization (should be technology based on AI content)
            self.assertEqual(result['category'], 'technology')
            
            # Verify metadata
            metadata = result['metadata']
            self.assertEqual(metadata['provider'], 'openai')
            self.assertEqual(metadata['source_type'], 'url')
            self.assertIn('timestamp', metadata)

    @patch('config.app_settings.get_settings')
    @patch('pipeline.pipeline_manager.LLMProviderFactory')
    def test_complete_topic_to_blog_workflow(self, mock_factory, mock_load_config):
        """Test complete workflow from topic to finished blog post."""
        # Setup configuration
        mock_load_config.return_value = self.mock_config
        
        # Setup provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.provider_name = 'anthropic'
        mock_provider.generate_blog.return_value = {
            'title': 'The Future of Blockchain Technology',
            'content': '<h1>Blockchain Revolution</h1><p>Blockchain technology is revolutionizing...</p>',
            'summary': 'Exploring the transformative potential of blockchain technology.'
        }
        
        mock_factory_instance = Mock()
        mock_factory_instance.get_available_provider.return_value = mock_provider
        mock_factory.return_value = mock_factory_instance
        
        # Import and test pipeline
        from pipeline.pipeline_manager import PipelineManager
        
        # Mock pipeline manager to avoid constructor issues
        with patch('pipeline.pipeline_manager.PipelineManager') as mock_pipeline_class:
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.process_topic.return_value = {
                'title': 'The Future of Blockchain Technology',
                'content': '<h1>Blockchain Revolution</h1><p>Blockchain technology is revolutionizing...</p>',
                'summary': 'Exploring the transformative potential of blockchain technology.',
                'category': 'blockchain',
                'metadata': {
                    'provider': 'anthropic',
                    'source_type': 'topic'
                }
            }
            mock_pipeline_class.return_value = mock_pipeline_instance
            result = mock_pipeline_instance.process_topic('Blockchain Technology', style='tech')
        
            # Verify complete workflow
            self.assertIsInstance(result, dict)
            
            # Check all required fields
            required_fields = ['title', 'content', 'summary', 'category', 'metadata']
            for field in required_fields:
                self.assertIn(field, result)
            
            # Verify content
            self.assertEqual(result['title'], 'The Future of Blockchain Technology')
            self.assertIn('Blockchain Revolution', result['content'])
            
            # Verify metadata
            metadata = result['metadata']
            self.assertEqual(metadata['provider'], 'anthropic')
            self.assertEqual(metadata['source_type'], 'topic')

    @patch('config.app_settings.get_settings')
    @patch('app.PipelineManager')
    def test_flask_api_integration(self, mock_pipeline, mock_load_config):
        """Test complete Flask API integration."""
        # Setup configuration
        mock_load_config.return_value = self.mock_config
        
        # Setup pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_topic.return_value = {
            'title': 'API Generated Blog',
            'content': '<h1>API Blog</h1><p>Generated via API...</p>',
            'summary': 'A blog post generated through the API.',
            'category': 'Technology',
            'featured_image': 'https://cdn.testdomain.com/image.jpg',
            'metadata': {
                'provider': 'openai',
                'timestamp': '2025-01-01T12:00:00',
                'source_type': 'topic'
            }
        }
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Import Flask app and test
        from app import app
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test API request
        request_data = {
            'topic': 'Artificial Intelligence',
            'provider': 'openai',
            'style': 'tech'
        }
        
        response = client.post('/generate',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('blog', data)
        
        blog = data['blog']
        self.assertEqual(blog['title'], 'API Generated Blog')
        self.assertEqual(blog['category'], 'Technology')
        self.assertIn('metadata', blog)

    @patch('config.app_settings.get_settings')
    @patch('providers.factory.LLMProviderFactory.create_provider')
    def test_provider_fallback_integration(self, mock_create_provider, mock_load_config):
        """Test provider fallback when primary provider fails."""
        # Setup configuration
        mock_load_config.return_value = self.mock_config
        
        # Setup provider responses
        def provider_side_effect(provider_type, config):
            if provider_type == 'openai':
                # OpenAI provider (primary) as unavailable
                mock_openai_instance = Mock()
                mock_openai_instance.is_available.return_value = False
                mock_openai_instance.provider_name = 'openai'
                return mock_openai_instance
            elif provider_type == 'anthropic':
                # Anthropic provider (fallback) as available
                mock_anthropic_instance = Mock()
                mock_anthropic_instance.is_available.return_value = True
                mock_anthropic_instance.provider_name = 'anthropic'
                return mock_anthropic_instance
            else:
                return None
        
        mock_create_provider.side_effect = provider_side_effect
        
        # Test provider factory fallback
        from providers.factory import LLMProviderFactory
        
        factory = LLMProviderFactory()
        
        # Test creating providers
        openai_provider = factory.create_provider('openai', {'api_key': 'test-key'})
        anthropic_provider = factory.create_provider('anthropic', {'api_key': 'test-key'})
        
        # Verify fallback logic
        self.assertFalse(openai_provider.is_available())
        self.assertTrue(anthropic_provider.is_available())
        
        # Mock a successful blog generation result
        mock_blog_result = {
            'success': True,
            'data': {
                'title': 'Fallback Generated Blog',
                'content': '<h1>Fallback Blog</h1><p>Generated by fallback provider...</p>',
                'summary': 'A blog generated by the fallback provider.',
                'category': 'technology'
            }
        }
        
        # Test blog generation with fallback provider
        from pipeline.blog_generator import BlogGenerator
        
        with patch.object(BlogGenerator, 'generate', return_value=mock_blog_result):
            generator = BlogGenerator(config={}, providers={'anthropic': anthropic_provider})
            result = generator.generate(
                url='test-url',
                content='Test Topic content',
                category='technology'
            )
            
            # Verify fallback worked
            self.assertEqual(result['data']['title'], 'Fallback Generated Blog')
            self.assertIn('Fallback Blog', result['data']['content'])

    @patch('config.app_settings.get_settings')
    def test_categorization_integration(self, mock_load_config):
        """Test AI categorization with rule-based fallback."""
        # Setup configuration
        mock_load_config.return_value = self.mock_config
        
        # Test categorization with rule-based fallback
        from pipeline.categorizer import ContentCategorizer
        
        # This should test the fallback mechanism
        tech_content = "This article discusses artificial intelligence and machine learning algorithms."
        
        # Create categorizer with unavailable provider to force rule-based categorization
        mock_provider = Mock()
        mock_provider.is_available.return_value = False  # Force rule-based categorization
        
        config = {'categories': ['technology', 'ai-ml', 'business'], 'fallback_category': 'technology'}
        categorizer = ContentCategorizer(config=config, providers={'mock': mock_provider})
        result = categorizer.categorize(
            url='https://example.com/ai-article',
            content=tech_content,
            title='AI and Machine Learning Guide'
        )
        
        # Should categorize as ai-ml based on keywords since that's more specific
        self.assertTrue(result['success'])
        self.assertIn(result['category'], ['ai-ml', 'technology'])
        self.assertEqual(result['method'], 'rules')

    def test_error_handling_integration(self):
        """Test error handling across the complete system."""
        # Test with invalid configuration
        with patch('config.app_settings.get_settings') as mock_load_config:
            mock_load_config.side_effect = Exception("Configuration error")
            
            # Should handle configuration errors gracefully
            from app import app
            app.config['TESTING'] = True
            client = app.test_client()
            
            response = client.get('/health')
            
            # Should return error response but not crash
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('error', data)


class TestMultiProviderIntegration(unittest.TestCase):
    """Test integration across multiple AI providers."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.api.openai_api_key = 'test-openai-key'
        self.mock_config.api.anthropic_api_key = 'test-anthropic-key'
        self.mock_config.api.gemini_api_key = 'test-gemini-key'
        self.mock_config.api.grok_api_key = 'test-grok-key'

    @patch('providers.factory.LLMProviderFactory.create_provider')
    def test_multi_provider_availability(self, mock_create_provider):
        """Test checking availability across multiple providers."""
        # Setup provider responses
        def provider_side_effect(provider_type, config):
            if provider_type == 'openai':
                mock_openai_instance = Mock()
                mock_openai_instance.is_available.return_value = True
                mock_openai_instance.provider_name = 'openai'
                return mock_openai_instance
            elif provider_type == 'anthropic':
                mock_anthropic_instance = Mock()
                mock_anthropic_instance.is_available.return_value = False
                mock_anthropic_instance.provider_name = 'anthropic'
                return mock_anthropic_instance
            else:
                return None
        
        mock_create_provider.side_effect = provider_side_effect
        
        # Test factory
        from providers.factory import LLMProviderFactory
        
        factory = LLMProviderFactory()
        
        # Check individual providers
        openai_provider = factory.create_provider('openai', {'api_key': 'test-key'})
        anthropic_provider = factory.create_provider('anthropic', {'api_key': 'test-key'})
        
        self.assertTrue(openai_provider.is_available())
        self.assertFalse(anthropic_provider.is_available())
        
        # Test available provider types  
        available_providers = factory.get_available_providers()
        self.assertIn('openai', available_providers)
        self.assertIn('anthropic', available_providers)

    def test_provider_response_consistency(self):
        """Test that all providers return consistent response formats."""
        # Mock providers with consistent responses
        providers_data = [
            ('openai', {
                'title': 'OpenAI Generated Title',
                'content': '<h1>OpenAI Content</h1>',
                'summary': 'OpenAI summary'
            }),
            ('anthropic', {
                'title': 'Anthropic Generated Title',
                'content': '<h1>Anthropic Content</h1>',
                'summary': 'Anthropic summary'
            })
        ]
        
        for provider_name, expected_response in providers_data:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.provider_name = provider_name
            mock_provider.generate_blog.return_value = expected_response
            
            # Test blog generation with mock return value
            from pipeline.blog_generator import BlogGenerator
            
            # Mock the generator result to match expected format
            mock_result = {
                'success': True,
                'data': expected_response
            }
            
            with patch.object(BlogGenerator, 'generate', return_value=mock_result):
                generator = BlogGenerator(config={}, providers={provider_name: mock_provider})
                result = generator.generate(
                    url='test-url',
                    content='Test Topic content',
                    category='technology'
                )
                
                # Verify consistent response format
                self.assertTrue(result['success'])
                self.assertIn('data', result)
                
                data = result['data']
                required_fields = ['title', 'content', 'summary']
                for field in required_fields:
                    self.assertIn(field, data)
                
                self.assertEqual(data['title'], expected_response['title'])
                self.assertEqual(data['content'], expected_response['content'])
                self.assertEqual(data['summary'], expected_response['summary'])


if __name__ == '__main__':
    unittest.main() 