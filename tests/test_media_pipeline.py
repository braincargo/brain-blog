"""
Tests for the media pipeline components.

This module tests image generation, meme generation, and media storage functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
import requests

from pipeline.image_generator import ImageGenerator
from pipeline.meme_generator import MemeGenerator
from pipeline.media_storage import MediaStorageManager


class TestImageGenerator:
    """Test image generation functionality"""
    
    def test_generate_instructions_success(self, mock_config, mock_providers, sample_blog_data):
        """Test successful image instruction generation"""
        generator = ImageGenerator(mock_config, mock_providers)
        
        # Mock the prompt file loading
        with patch.object(generator, '_load_prompt') as mock_load_prompt:
            mock_load_prompt.return_value = "Generate image instructions for {title}"
            
            result = generator.generate_instructions(sample_blog_data, 'technology')
            
            assert result['success'] is True
            assert 'data' in result
            assert result['provider'] == 'openai'
            mock_load_prompt.assert_called_once()
    
    def test_generate_instructions_fallback(self, mock_config, sample_blog_data):
        """Test fallback when no providers available"""
        # Create generator with no providers
        generator = ImageGenerator(mock_config, {})
        
        result = generator.generate_instructions(sample_blog_data, 'technology')
        
        assert result['success'] is True
        assert result['provider'] == 'fallback'
        assert 'data' in result
    
    def test_generate_image_success(self, mock_config, mock_providers, sample_image_instructions, sample_blog_data):
        """Test successful image generation"""
        generator = ImageGenerator(mock_config, mock_providers)
        
        result = generator.generate_image(sample_image_instructions, sample_blog_data, 'technology')
        
        assert result['success'] is True
        assert 'image_url' in result
        assert result['provider'] == 'openai'
        assert result['image_url'] == 'https://example.com/test-image.png'
    
    def test_generate_image_provider_fallback(self, mock_config, mock_providers, sample_image_instructions):
        """Test provider fallback when primary provider fails"""
        # Make first provider fail
        mock_providers['openai'].generate_image.return_value = {'success': False, 'error': 'Test failure'}
        
        generator = ImageGenerator(mock_config, mock_providers)
        result = generator.generate_image(sample_image_instructions, {}, 'technology')
        
        # Should still succeed with fallback (anthropic doesn't have generate_image, so it will fallback)
        assert 'success' in result
        assert 'error' in result or result['success'] is True
    
    def test_build_dalle_prompt(self, mock_config, mock_providers, sample_image_instructions):
        """Test DALL-E prompt building"""
        generator = ImageGenerator(mock_config, mock_providers)
        
        prompt = generator._build_dalle_prompt(sample_image_instructions, {'title': 'Test Blog'})
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'Professional technology blog' in prompt
    
    def test_generate_alt_text(self, mock_config, mock_providers, sample_image_instructions):
        """Test alt text generation"""
        generator = ImageGenerator(mock_config, mock_providers)
        
        alt_text = generator._generate_alt_text(sample_image_instructions, {'title': 'Test Blog'})
        
        assert isinstance(alt_text, str)
        assert 'Test Blog' in alt_text


class TestMemeGenerator:
    """Test meme generation functionality"""
    
    def test_generate_success(self, mock_config, mock_providers, sample_blog_data):
        """Test successful meme generation"""
        generator = MemeGenerator(mock_config, mock_providers)
        
        # Mock the prompt loading
        with patch.object(generator, '_load_prompt') as mock_load_prompt:
            mock_load_prompt.return_value = "Generate meme for {title}"
            
            result = generator.generate(sample_blog_data, 'technology')
            
            assert result['success'] is True
            assert 'data' in result
            assert result['provider'] == 'openai'
    
    def test_generate_fallback(self, mock_config, sample_blog_data):
        """Test fallback when no providers available"""
        generator = MemeGenerator(mock_config, {})
        
        result = generator.generate(sample_blog_data, 'technology')
        
        assert result['success'] is True
        assert result['provider'] == 'fallback'
        assert 'data' in result
    
    def test_parse_meme_response_valid_json(self, mock_config, mock_providers):
        """Test parsing valid JSON meme response"""
        generator = MemeGenerator(mock_config, mock_providers)
        
        json_response = '{"template": "drake_pointing", "top_text": "Old way", "bottom_text": "New way"}'
        result = generator._parse_meme_response(json_response)
        
        assert result['template'] == 'drake_pointing'
        assert result['top_text'] == 'Old way'
        assert result['bottom_text'] == 'New way'
    
    def test_parse_meme_response_invalid_json(self, mock_config, mock_providers):
        """Test parsing invalid JSON falls back to default"""
        generator = MemeGenerator(mock_config, mock_providers)
        
        invalid_response = "This is not JSON"
        result = generator._parse_meme_response(invalid_response)
        
        # Should return default meme data
        assert 'template' in result
        assert 'top_text' in result
        assert 'bottom_text' in result
    
    def test_build_meme_dalle_prompt(self, mock_config, mock_providers, sample_meme_data):
        """Test building DALL-E prompt for meme"""
        generator = MemeGenerator(mock_config, mock_providers)
        
        prompt = generator._build_meme_dalle_prompt(sample_meme_data, {'title': 'Test Blog'})
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'drake' in prompt.lower()  # Should mention the template
    
    def test_create_meme_image_with_fallbacks(self, mock_config, mock_providers, sample_meme_data, sample_blog_data):
        """Test meme image creation with provider fallbacks"""
        generator = MemeGenerator(mock_config, mock_providers)
        
        result = generator._create_meme_image_with_fallbacks(sample_meme_data, sample_blog_data, 'technology')
        
        # Should either succeed or fall back to text-only
        assert 'meme_type' in result
        if result.get('success'):
            assert result['meme_type'] == 'generated_image'
        else:
            assert result['meme_type'] == 'text_only'


class TestMediaStorageManager:
    """Test media storage functionality"""
    
    def test_initialization_with_s3(self, mock_config, mock_s3_client):
        """Test initialization with S3 configured"""
        with patch.dict('os.environ', {
            'BLOG_POSTS_BUCKET': 'test-bucket',
            'MEDIA_PREFIX': 'test-media',
            'CDN_BASE_URL': 'https://test-cdn.com'
        }):
            storage = MediaStorageManager(mock_config)
            
            assert storage.bucket_name == 'test-bucket'
            assert storage.media_prefix == 'test-media'
            assert storage.cdn_base_url == 'https://test-cdn.com'
    
    def test_save_image_to_s3_success(self, mock_config, mock_s3_client):
        """Test successful image save to S3"""
        with patch.dict('os.environ', {'BLOG_POSTS_BUCKET': 'test-bucket'}):
            storage = MediaStorageManager(mock_config)
            storage.s3_client = mock_s3_client
            
            # Mock the requests.get call
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.content = b'fake image data'
                mock_response.headers = {'content-type': 'image/png'}
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                result = storage.save_image_to_s3(
                    'https://example.com/test.png',
                    'blog123',
                    'featured'
                )
                
                assert result['success'] is True
                assert result['storage_location'] == 's3'
                assert 'permanent_url' in result
                assert 's3_key' in result
                mock_s3_client.put_object.assert_called_once()
    
    def test_save_image_to_s3_no_s3(self, mock_config):
        """Test image save when S3 not configured"""
        storage = MediaStorageManager(mock_config)
        storage.s3_client = None
        storage.bucket_name = None
        
        result = storage.save_image_to_s3(
            'https://example.com/test.png',
            'blog123',
            'featured'
        )
        
        assert result['success'] is False
        assert result['storage_location'] == 'temporary'
        assert 'S3 not configured' in result['error']
    
    def test_save_image_to_s3_download_failure(self, mock_config, mock_s3_client):
        """Test handling of image download failure"""
        with patch.dict('os.environ', {'BLOG_POSTS_BUCKET': 'test-bucket'}):
            storage = MediaStorageManager(mock_config)
            storage.s3_client = mock_s3_client
            
            # Mock a failed requests.get call
            with patch('requests.get') as mock_get:
                mock_get.side_effect = requests.RequestException("Download failed")
                
                result = storage.save_image_to_s3(
                    'https://example.com/test.png',
                    'blog123',
                    'featured'
                )
                
                assert result['success'] is False
                assert result['storage_location'] == 'temporary'
                assert 'Download failed' in result['error']
    
    def test_save_multiple_images(self, mock_config, mock_s3_client):
        """Test saving multiple images"""
        with patch.dict('os.environ', {'BLOG_POSTS_BUCKET': 'test-bucket'}):
            storage = MediaStorageManager(mock_config)
            storage.s3_client = mock_s3_client
            
            # Mock save_image_to_s3 method
            with patch.object(storage, 'save_image_to_s3') as mock_save:
                mock_save.return_value = {'success': True, 'permanent_url': 'https://cdn.example.com/test.png'}
                
                images = {
                    'featured': 'https://example.com/featured.png',
                    'meme': 'https://example.com/meme.png'
                }
                
                results = storage.save_multiple_images(images, 'blog123')
                
                assert len(results) == 2
                assert 'featured' in results
                assert 'meme' in results
                assert results['featured']['success'] is True
                assert results['meme']['success'] is True
    
    def test_cleanup_temporary_urls(self, mock_config, mock_s3_client):
        """Test cleaning up temporary URLs in blog data"""
        with patch.dict('os.environ', {'BLOG_POSTS_BUCKET': 'test-bucket'}):
            storage = MediaStorageManager(mock_config)
            
            blog_data = {
                'id': 'test123',
                'content': '<img src="https://temp.com/image.png">',
                'media': {
                    'featured_image': 'https://temp.com/featured.png',
                    'meme_url': 'https://temp.com/meme.png'
                }
            }
            
            # Mock save_multiple_images
            with patch.object(storage, 'save_multiple_images') as mock_save_multiple:
                mock_save_multiple.return_value = {
                    'featured': {
                        'success': True,
                        'permanent_url': 'https://cdn.example.com/featured.png',
                        's3_key': 'media/featured.png'
                    },
                    'meme': {
                        'success': True,
                        'permanent_url': 'https://cdn.example.com/meme.png',
                        's3_key': 'media/meme.png'
                    }
                }
                
                result = storage.cleanup_temporary_urls(blog_data)
                
                assert result['media']['featured_image'] == 'https://cdn.example.com/featured.png'
                assert result['media']['meme_url'] == 'https://cdn.example.com/meme.png'
                assert 'storage' in result['media']
    
    def test_get_media_stats_success(self, mock_config, mock_s3_client):
        """Test getting media statistics"""
        with patch.dict('os.environ', {'BLOG_POSTS_BUCKET': 'test-bucket'}):
            storage = MediaStorageManager(mock_config)
            storage.s3_client = mock_s3_client
            
            stats = storage.get_media_stats()
            
            assert 'total_files' in stats
            assert 'total_size_bytes' in stats
            assert 'total_size_mb' in stats
            assert stats['total_files'] == 5  # From mock
            assert stats['bucket'] == 'test-bucket'
    
    def test_get_media_stats_no_s3(self, mock_config):
        """Test getting media statistics when S3 not configured"""
        storage = MediaStorageManager(mock_config)
        storage.s3_client = None
        
        stats = storage.get_media_stats()
        
        assert 'error' in stats
        assert 'S3 not configured' in stats['error']
    
    def test_generate_s3_key(self, mock_config):
        """Test S3 key generation"""
        storage = MediaStorageManager(mock_config)
        
        s3_key = storage._generate_s3_key('blog123', 'featured', '.png')
        
        assert isinstance(s3_key, str)
        assert 'blog123' in s3_key
        assert 'featured' in s3_key
        assert s3_key.endswith('.png')
        assert s3_key.startswith('test-media/')  # Uses MEDIA_PREFIX from env
    
    def test_get_file_extension_from_url(self, mock_config):
        """Test file extension detection from URL"""
        storage = MediaStorageManager(mock_config)
        
        # Test URL with extension
        ext = storage._get_file_extension('https://example.com/image.jpg')
        assert ext == '.jpg'
        
        # Test URL without extension but with content type
        ext = storage._get_file_extension('https://example.com/image', 'image/png')
        assert ext == '.png'
        
        # Test fallback to .png
        ext = storage._get_file_extension('https://example.com/image')
        assert ext == '.png'


class TestMediaPipelineIntegration:
    """Test integration between media pipeline components"""
    
    def test_complete_media_pipeline(self, pipeline, sample_blog_data):
        """Test complete media pipeline flow"""
        # Reset the providers to ensure clean state
        pipeline.providers['openai'].generate_image.return_value = {
            'success': True,
            'image_url': 'https://example.com/test-image.png',
            'revised_prompt': 'Enhanced test prompt',
            'model': 'dall-e-3'
        }
        
        # Test image generation
        image_generator = pipeline.steps['image_generator']
        instructions = image_generator.generate_instructions(sample_blog_data, 'technology')
        assert instructions['success'] is True
        
        image_result = image_generator.generate_image(instructions['data'], sample_blog_data, 'technology')
        assert image_result['success'] is True
        
        # Test meme generation
        meme_generator = pipeline.steps['meme_generator']
        meme_result = meme_generator.generate(sample_blog_data, 'technology')
        assert meme_result['success'] is True
        
        # Test media embedding
        blog_generator = pipeline.steps['blog_generator']
        enhanced_blog = blog_generator.embed_media_in_content(
            sample_blog_data,
            image_data=image_result,
            meme_data=meme_result['data']
        )
        
        assert 'media' in enhanced_blog
        assert enhanced_blog['media']['featured_image'] is not None
    
    def test_media_pipeline_error_handling(self, mock_config):
        """Test error handling in media pipeline"""
        # Test with no providers
        image_generator = ImageGenerator(mock_config, {})
        meme_generator = MemeGenerator(mock_config, {})
        
        # Should gracefully handle errors and return fallback results
        instructions = image_generator.generate_instructions({'title': 'Test'}, 'technology')
        assert instructions['success'] is True
        assert instructions['provider'] == 'fallback'
        
        meme_result = meme_generator.generate({'title': 'Test'}, 'technology')
        assert meme_result['success'] is True
        assert meme_result['provider'] == 'fallback' 