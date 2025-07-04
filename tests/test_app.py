"""
Unit tests for the main Flask application.

Tests the Flask app endpoints, request handling, and response formatting.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestFlaskApp(unittest.TestCase):
    """Test the main Flask application."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')

    @patch('config.app_settings.get_settings')
    def test_health_endpoint_with_providers(self, mock_load_config):
        """Test health endpoint with provider availability."""
        # Mock configuration
        mock_config = Mock()
        mock_config.api.openai_api_key = 'test-key'
        mock_config.api.anthropic_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        with patch('app.LLMProviderFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_factory.return_value.create_provider.return_value = mock_provider
            
            response = self.client.get('/health')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertIn('providers_available', data)

    @patch('app.PipelineManager')
    @patch('config.app_settings.get_settings')
    def test_generate_endpoint_url(self, mock_load_config, mock_pipeline):
        """Test blog generation from URL."""
        # Mock configuration
        mock_config = Mock()
        mock_config.api.openai_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_url.return_value = {
            'title': 'Test Blog',
            'content': 'Test content',
            'summary': 'Test summary',
            'category': 'Technology',
            'metadata': {'provider': 'openai'}
        }
        mock_pipeline.return_value = mock_pipeline_instance
        
        request_data = {
            'url': 'https://example.com/article',
            'provider': 'openai'
        }
        
        response = self.client.post('/generate',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('blog', data)
        self.assertEqual(data['blog']['title'], 'Test Blog')

    @patch('app.PipelineManager')
    @patch('config.app_settings.get_settings')
    def test_generate_endpoint_topic(self, mock_load_config, mock_pipeline):
        """Test blog generation from topic."""
        # Mock configuration
        mock_config = Mock()
        mock_config.api.anthropic_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_topic.return_value = {
            'title': 'Brain Blog',
            'content': 'AI content',
            'summary': 'AI summary',
            'category': 'Technology',
            'metadata': {'provider': 'anthropic'}
        }
        mock_pipeline.return_value = mock_pipeline_instance
        
        request_data = {
            'topic': 'Artificial Intelligence',
            'provider': 'anthropic',
            'style': 'tech'
        }
        
        response = self.client.post('/generate',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('blog', data)
        self.assertEqual(data['blog']['title'], 'Brain Blog')

    @patch('app.PipelineManager')
    @patch('config.app_settings.get_settings')
    def test_generate_endpoint_content(self, mock_load_config, mock_pipeline):
        """Test blog generation from custom content."""
        # Mock configuration
        mock_config = Mock()
        mock_config.api.openai_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_content.return_value = {
            'title': 'Custom Blog',
            'content': 'Custom content',
            'summary': 'Custom summary',
            'category': 'General',
            'metadata': {'provider': 'openai'}
        }
        mock_pipeline.return_value = mock_pipeline_instance
        
        request_data = {
            'content': 'Custom content to transform',
            'title': 'Custom Title',
            'provider': 'openai'
        }
        
        response = self.client.post('/generate',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('blog', data)
        self.assertEqual(data['blog']['title'], 'Custom Blog')

    def test_generate_endpoint_missing_input(self):
        """Test generate endpoint with missing input data."""
        request_data = {
            'provider': 'openai'
            # Missing url, topic, or content
        }
        
        response = self.client.post('/generate',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_generate_endpoint_invalid_json(self):
        """Test generate endpoint with invalid JSON."""
        response = self.client.post('/generate',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    @patch('app.PipelineManager')
    @patch('config.app_settings.get_settings')
    def test_generate_endpoint_provider_error(self, mock_load_config, mock_pipeline):
        """Test generate endpoint when provider fails."""
        # Mock configuration
        mock_config = Mock()
        mock_config.api.openai_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        # Mock pipeline to raise an exception
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_topic.side_effect = Exception("Provider error")
        mock_pipeline.return_value = mock_pipeline_instance
        
        request_data = {
            'topic': 'Test Topic',
            'provider': 'openai'
        }
        
        response = self.client.post('/generate',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_providers_status_endpoint(self):
        """Test the providers status endpoint."""
        with patch('config.app_settings.get_settings') as mock_load_config:
            mock_config = Mock()
            mock_config.api.openai_api_key = 'test-key'
            mock_config.api.anthropic_api_key = ''
            mock_load_config.return_value = mock_config
            
            with patch('app.LLMProviderFactory') as mock_factory:
                mock_factory_instance = Mock()
                
                # Mock OpenAI provider as available
                mock_openai = Mock()
                mock_openai.is_available.return_value = True
                
                # Mock Anthropic provider as unavailable
                mock_anthropic = Mock()
                mock_anthropic.is_available.return_value = False
                
                mock_factory_instance.create_provider.side_effect = [mock_openai, mock_anthropic]
                mock_factory.return_value = mock_factory_instance
                
                response = self.client.get('/providers/status')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                
                self.assertIn('providers', data)
                self.assertTrue(data['providers']['openai'])
                self.assertFalse(data['providers']['anthropic'])

    def test_webhook_endpoint_get(self):
        """Test webhook endpoint GET request."""
        response = self.client.get('/webhook')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Brain Blog Generator Webhook', response.data.decode())

    @patch('app.PipelineManager')
    @patch('config.app_settings.get_settings')
    def test_webhook_endpoint_post_authorized(self, mock_load_config, mock_pipeline):
        """Test webhook endpoint POST with authorized phone."""
        # Mock configuration with phone authorization
        mock_config = Mock()
        mock_config.security.enable_phone_auth = True
        mock_config.security.authorized_phone = '1234567890'
        mock_config.api.openai_api_key = 'test-key'
        mock_load_config.return_value = mock_config
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_url.return_value = {
            'title': 'Webhook Blog',
            'content': 'Webhook content',
            'summary': 'Webhook summary'
        }
        mock_pipeline.return_value = mock_pipeline_instance
        
        form_data = {
            'From': '+1234567890',
            'Body': 'Generate blog from https://example.com/article'
        }
        
        response = self.client.post('/webhook', data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully generated', response.data.decode())

    @patch('config.app_settings.get_settings')
    def test_webhook_endpoint_post_unauthorized(self, mock_load_config):
        """Test webhook endpoint POST with unauthorized phone."""
        # Mock configuration with phone authorization
        mock_config = Mock()
        mock_config.security.enable_phone_auth = True
        mock_config.security.authorized_phone = '1234567890'
        mock_load_config.return_value = mock_config
        
        form_data = {
            'From': '+9876543210',  # Different phone number
            'Body': 'Generate blog from https://example.com/article'
        }
        
        response = self.client.post('/webhook', data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Unauthorized', response.data.decode())

    def test_webhook_endpoint_no_urls(self):
        """Test webhook endpoint with no URLs in message."""
        with patch('config.app_settings.get_settings') as mock_load_config:
            mock_config = Mock()
            mock_config.security.enable_phone_auth = False
            mock_load_config.return_value = mock_config
            
            form_data = {
                'From': '+1234567890',
                'Body': 'This message has no URLs'
            }
            
            response = self.client.post('/webhook', data=form_data)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('No URLs found', response.data.decode())

    def test_404_error_handler(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Endpoint not found')

    def test_500_error_handler(self):
        """Test 500 error handling."""
        with patch('config.app_settings.get_settings') as mock_load_config:
            mock_load_config.side_effect = Exception("Configuration error")
            
            response = self.client.get('/health')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            
            self.assertFalse(data['success'])
            self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main() 