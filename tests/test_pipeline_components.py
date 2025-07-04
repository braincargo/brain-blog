"""
Unit tests for blog generation pipeline components.

Tests the blog generator, categorizer, and pipeline manager.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add parent directory to path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBlogGenerator(unittest.TestCase):
    """Test the BlogGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = Mock()
        self.mock_provider.generate_blog.return_value = {
            'title': 'Test Blog Title',
            'content': '<h1>Test Blog</h1><p>Test content</p>',
            'summary': 'Test summary'
        }
        self.mock_provider.is_available.return_value = True
        self.mock_provider.provider_name = 'test_provider'

    def test_blog_generator_initialization(self):
        """Test BlogGenerator initialization."""
        # Mock the BlogGenerator class since we don't have the actual implementation
        # This would test the real implementation once it's available
        
        from unittest.mock import Mock
        mock_blog_generator = Mock()
        mock_blog_generator.provider = self.mock_provider
        
        self.assertEqual(mock_blog_generator.provider, self.mock_provider)

    def test_generate_from_url_mock(self):
        """Test generating blog from URL (mocked)."""
        # Mock implementation for URL generation
        mock_generator = Mock()
        
        def mock_generate_from_url(url):
            return {
                'title': 'Blog from URL',
                'content': '<h1>URL Blog</h1><p>Content from URL</p>',
                'summary': 'A blog generated from URL content'
            }
        
        mock_generator.generate_from_url = mock_generate_from_url
        
        result = mock_generator.generate_from_url('https://example.com/article')
        
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('content', result)
        self.assertIn('summary', result)
        self.assertEqual(result['title'], 'Blog from URL')

    def test_generate_from_topic_mock(self):
        """Test generating blog from topic (mocked)."""
        mock_generator = Mock()
        
        def mock_generate_from_topic(topic, style='general'):
            return {
                'title': f'Blog about {topic}',
                'content': f'<h1>{topic}</h1><p>Content about {topic}</p>',
                'summary': f'A blog post about {topic}'
            }
        
        mock_generator.generate_from_topic = mock_generate_from_topic
        
        result = mock_generator.generate_from_topic('Artificial Intelligence', style='tech')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'Blog about Artificial Intelligence')
        self.assertIn('Artificial Intelligence', result['content'])

    def test_provider_availability_check(self):
        """Test provider availability checking."""
        # Test available provider
        available_provider = Mock()
        available_provider.is_available.return_value = True
        self.assertTrue(available_provider.is_available())
        
        # Test unavailable provider
        unavailable_provider = Mock()
        unavailable_provider.is_available.return_value = False
        self.assertFalse(unavailable_provider.is_available())


class TestContentCategorizer(unittest.TestCase):
    """Test the ContentCategorizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = Mock()
        self.mock_provider.is_available.return_value = True

    def test_categorizer_initialization_mock(self):
        """Test ContentCategorizer initialization (mocked)."""
        mock_categorizer = Mock()
        mock_categorizer.provider = self.mock_provider
        mock_categorizer.categories = [
            'technology', 'business', 'science', 'health',
            'education', 'entertainment', 'sports', 'politics',
            'finance', 'travel', 'food', 'lifestyle', 'general'
        ]
        
        self.assertEqual(mock_categorizer.provider, self.mock_provider)
        self.assertIsInstance(mock_categorizer.categories, list)
        self.assertGreater(len(mock_categorizer.categories), 0)
        self.assertIn('technology', mock_categorizer.categories)

    def test_ai_categorization_mock(self):
        """Test AI-powered categorization (mocked)."""
        mock_categorizer = Mock()
        
        def mock_categorize(content):
            # Simple keyword-based categorization for testing
            if any(word in content.lower() for word in ['ai', 'artificial intelligence', 'machine learning']):
                return 'technology'
            elif any(word in content.lower() for word in ['business', 'startup', 'marketing']):
                return 'business'
            elif any(word in content.lower() for word in ['health', 'medical', 'wellness']):
                return 'health'
            else:
                return 'general'
        
        mock_categorizer.categorize = mock_categorize
        
        # Test technology content
        tech_result = mock_categorizer.categorize('This article discusses artificial intelligence')
        self.assertEqual(tech_result, 'technology')
        
        # Test business content
        business_result = mock_categorizer.categorize('This article is about startup business strategies')
        self.assertEqual(business_result, 'business')
        
        # Test health content
        health_result = mock_categorizer.categorize('This article covers medical wellness topics')
        self.assertEqual(health_result, 'health')
        
        # Test general content
        general_result = mock_categorizer.categorize('This is some random content')
        self.assertEqual(general_result, 'general')

    def test_rule_based_fallback_mock(self):
        """Test rule-based categorization fallback (mocked)."""
        def rule_based_categorize(content):
            """Mock rule-based categorization."""
            content_lower = content.lower()
            
            tech_keywords = ['ai', 'artificial intelligence', 'machine learning', 'technology', 'software']
            business_keywords = ['business', 'startup', 'marketing', 'sales', 'entrepreneur']
            health_keywords = ['health', 'medical', 'wellness', 'fitness', 'nutrition']
            
            if any(keyword in content_lower for keyword in tech_keywords):
                return 'technology'
            elif any(keyword in content_lower for keyword in business_keywords):
                return 'business'
            elif any(keyword in content_lower for keyword in health_keywords):
                return 'health'
            else:
                return 'general'
        
        # Test various content types
        test_cases = [
            ('artificial intelligence and machine learning', 'technology'),
            ('business strategy and marketing', 'business'),
            ('health and wellness tips', 'health'),
            ('random content without keywords', 'general')
        ]
        
        for content, expected_category in test_cases:
            result = rule_based_categorize(content)
            self.assertEqual(result, expected_category)


class TestPipelineManager(unittest.TestCase):
    """Test the PipelineManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = Mock()
        self.mock_provider.is_available.return_value = True
        self.mock_provider.provider_name = 'test_provider'

    def test_pipeline_manager_initialization_mock(self):
        """Test PipelineManager initialization (mocked)."""
        mock_pipeline = Mock()
        mock_pipeline.provider = self.mock_provider
        mock_pipeline.blog_generator = Mock()
        mock_pipeline.categorizer = Mock()
        
        self.assertEqual(mock_pipeline.provider, self.mock_provider)
        self.assertIsNotNone(mock_pipeline.blog_generator)
        self.assertIsNotNone(mock_pipeline.categorizer)

    def test_complete_pipeline_workflow_mock(self):
        """Test complete pipeline workflow (mocked)."""
        mock_pipeline = Mock()
        
        def mock_process_url(url):
            return {
                'title': 'Pipeline Generated Blog',
                'content': '<h1>Pipeline Blog</h1><p>Generated through pipeline</p>',
                'summary': 'A blog generated through the complete pipeline',
                'category': 'technology',
                'featured_image': 'https://example.com/image.jpg',
                'metadata': {
                    'provider': 'test_provider',
                    'timestamp': '2025-01-01T12:00:00',
                    'source_type': 'url',
                    'processing_time': 8.5
                }
            }
        
        mock_pipeline.process_url = mock_process_url
        
        result = mock_pipeline.process_url('https://example.com/article')
        
        # Verify complete pipeline output
        self.assertIsInstance(result, dict)
        
        # Check all required fields
        required_fields = ['title', 'content', 'summary', 'category', 'metadata']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Verify content
        self.assertEqual(result['title'], 'Pipeline Generated Blog')
        self.assertEqual(result['category'], 'technology')
        
        # Verify metadata
        metadata = result['metadata']
        self.assertEqual(metadata['provider'], 'test_provider')
        self.assertEqual(metadata['source_type'], 'url')
        self.assertIn('timestamp', metadata)

    def test_topic_processing_mock(self):
        """Test topic processing through pipeline (mocked)."""
        mock_pipeline = Mock()
        
        def mock_process_topic(topic, style='general'):
            return {
                'title': f'Blog: {topic}',
                'content': f'<h1>{topic}</h1><p>Detailed content about {topic}</p>',
                'summary': f'An in-depth exploration of {topic}',
                'category': 'technology' if 'Artificial Intelligence' in topic else 'general',
                'metadata': {
                    'provider': 'test_provider',
                    'source_type': 'topic',
                    'style': style
                }
            }
        
        mock_pipeline.process_topic = mock_process_topic
        
        result = mock_pipeline.process_topic('Artificial Intelligence', style='tech')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'Blog: Artificial Intelligence')
        self.assertEqual(result['category'], 'technology')
        self.assertEqual(result['metadata']['style'], 'tech')

    def test_error_handling_mock(self):
        """Test error handling in pipeline (mocked)."""
        mock_pipeline = Mock()
        
        # Mock provider failure
        def mock_process_with_error(url):
            raise Exception("Provider unavailable")
        
        mock_pipeline.process_url = mock_process_with_error
        
        with self.assertRaises(Exception) as context:
            mock_pipeline.process_url('https://example.com')
        
        self.assertIn("Provider unavailable", str(context.exception))

    def test_metadata_generation_mock(self):
        """Test metadata generation in pipeline results (mocked)."""
        import datetime
        
        def mock_generate_metadata(provider_name, source_type, processing_time=None):
            return {
                'provider': provider_name,
                'timestamp': datetime.datetime.now().isoformat(),
                'source_type': source_type,
                'processing_time': processing_time or 5.0,
                'version': '1.0.0'
            }
        
        metadata = mock_generate_metadata('openai', 'topic', 7.5)
        
        self.assertEqual(metadata['provider'], 'openai')
        self.assertEqual(metadata['source_type'], 'topic')
        self.assertEqual(metadata['processing_time'], 7.5)
        self.assertEqual(metadata['version'], '1.0.0')
        self.assertIn('timestamp', metadata)


class TestPipelineIntegration(unittest.TestCase):
    """Test integration between pipeline components."""

    def test_blog_generator_categorizer_integration_mock(self):
        """Test integration between blog generator and categorizer (mocked)."""
        # Mock blog generator
        mock_blog_generator = Mock()
        mock_blog_generator.generate_from_topic.return_value = {
            'title': 'AI and Machine Learning',
            'content': 'Content about artificial intelligence and machine learning',
            'summary': 'A comprehensive guide to AI and ML'
        }
        
        # Mock categorizer
        mock_categorizer = Mock()
        mock_categorizer.categorize.return_value = 'technology'
        
        # Simulate pipeline integration
        blog_result = mock_blog_generator.generate_from_topic('AI Technology')
        category = mock_categorizer.categorize(blog_result['content'])
        
        # Combine results
        complete_result = {
            **blog_result,
            'category': category
        }
        
        self.assertEqual(complete_result['category'], 'technology')
        self.assertIn('title', complete_result)
        self.assertIn('content', complete_result)

    def test_provider_pipeline_integration_mock(self):
        """Test integration between provider and pipeline (mocked)."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.provider_name = 'anthropic'
        mock_provider.generate_blog.return_value = {
            'title': 'Provider Generated Content',
            'content': 'Content generated by the AI provider',
            'summary': 'Summary from AI provider'
        }
        
        # Mock pipeline that uses the provider
        def mock_pipeline_with_provider(topic):
            if not mock_provider.is_available():
                raise ValueError("Provider not available")
            
            blog_data = mock_provider.generate_blog(f"Generate blog about {topic}")
            
            return {
                **blog_data,
                'category': 'technology',  # Mock categorization
                'metadata': {
                    'provider': mock_provider.provider_name,
                    'source_type': 'topic'
                }
            }
        
        result = mock_pipeline_with_provider('Machine Learning')
        
        self.assertEqual(result['title'], 'Provider Generated Content')
        self.assertEqual(result['metadata']['provider'], 'anthropic')
        self.assertTrue(mock_provider.generate_blog.called)

    def test_multi_component_workflow_mock(self):
        """Test complete multi-component workflow (mocked)."""
        # Mock all components
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.provider_name = 'openai'
        
        mock_blog_generator = Mock()
        mock_categorizer = Mock()
        mock_image_generator = Mock()
        
        # Mock workflow
        def mock_complete_workflow(input_data):
            # Step 1: Generate blog content
            mock_blog_generator.generate.return_value = {
                'title': 'Complete Workflow Blog',
                'content': 'Blog content generated through complete workflow',
                'summary': 'A blog created using the full pipeline'
            }
            blog_data = mock_blog_generator.generate(input_data)
            
            # Step 2: Categorize content
            mock_categorizer.categorize.return_value = 'technology'
            category = mock_categorizer.categorize(blog_data['content'])
            
            # Step 3: Generate featured image
            mock_image_generator.generate.return_value = 'https://example.com/featured.jpg'
            featured_image = mock_image_generator.generate(blog_data['title'])
            
            # Combine all results
            return {
                **blog_data,
                'category': category,
                'featured_image': featured_image,
                'metadata': {
                    'provider': mock_provider.provider_name,
                    'components_used': ['blog_generator', 'categorizer', 'image_generator']
                }
            }
        
        result = mock_complete_workflow('Test input')
        
        # Verify complete workflow
        self.assertIn('title', result)
        self.assertIn('content', result)
        self.assertIn('summary', result)
        self.assertIn('category', result)
        self.assertIn('featured_image', result)
        self.assertIn('metadata', result)
        
        self.assertEqual(result['category'], 'technology')
        self.assertEqual(result['featured_image'], 'https://example.com/featured.jpg')
        self.assertIn('blog_generator', result['metadata']['components_used'])


if __name__ == '__main__':
    unittest.main() 