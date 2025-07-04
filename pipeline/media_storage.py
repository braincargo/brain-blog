"""
Media Storage Manager - Handles uploading and managing media files in S3
"""

import logging
import os
import uuid
import requests
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import mimetypes

logger = logging.getLogger(__name__)


class MediaStorageManager:
    """Manages media storage and URL handling for blog posts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.s3_client = None
        self.bucket_name = os.environ.get('BLOG_POSTS_BUCKET')
        self.media_prefix = os.environ.get('MEDIA_PREFIX', 'media')
        self.cdn_base_url = os.environ.get('CDN_BASE_URL', 'https://braincargo.com')
        
        # Initialize S3 client
        self._initialize_s3()
    
    def _initialize_s3(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client('s3')
            logger.info("✅ S3 client initialized for media storage")
        except Exception as e:
            logger.error(f"❌ S3 client initialization failed: {str(e)}")
            self.s3_client = None
    
    def save_image_to_s3(self, image_url: str, blog_id: str, image_type: str = 'featured') -> Dict[str, Any]:
        """
        Download image from temporary URL and save to S3
        
        Args:
            image_url: Temporary URL of the generated image
            blog_id: Blog post ID for organizing storage
            image_type: Type of image (featured, meme, thumbnail)
            
        Returns:
            Dict with permanent S3 URL and metadata
        """
        if not self.s3_client or not self.bucket_name:
            logger.warning("⚠️ S3 not configured, returning temporary URL")
            return {
                'success': False,
                'permanent_url': image_url,  # Fallback to temporary URL
                'storage_location': 'temporary',
                'error': 'S3 not configured'
            }
        
        try:
            # Download image from temporary URL
            logger.info(f"📥 Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Generate S3 key
            file_extension = self._get_file_extension(image_url, response.headers.get('content-type'))
            s3_key = self._generate_s3_key(blog_id, image_type, file_extension)
            
            # Upload to S3
            content_type = response.headers.get('content-type', 'image/png')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=response.content,
                ContentType=content_type,
                Metadata={
                    'blog-id': blog_id,
                    'image-type': image_type,
                    'original-url': image_url,
                    'uploaded-at': datetime.now(timezone.utc).isoformat(),
                    'source': 'BrainCargo'
                }
            )
            
            # Generate permanent URL
            permanent_url = f"{self.cdn_base_url}/{s3_key}"
            
            logger.info(f"✅ Image saved to S3: {s3_key}")
            
            return {
                'success': True,
                'permanent_url': permanent_url,
                's3_key': s3_key,
                'storage_location': 's3',
                'content_type': content_type,
                'file_size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save image to S3: {str(e)}")
            return {
                'success': False,
                'permanent_url': image_url,  # Fallback to temporary URL
                'storage_location': 'temporary',
                'error': str(e)
            }
    
    def save_multiple_images(self, images: Dict[str, str], blog_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Save multiple images to S3
        
        Args:
            images: Dict mapping image type to URL
            blog_id: Blog post ID
            
        Returns:
            Dict mapping image type to storage results
        """
        results = {}
        
        for image_type, image_url in images.items():
            if image_url:
                results[image_type] = self.save_image_to_s3(image_url, blog_id, image_type)
            else:
                results[image_type] = {
                    'success': False,
                    'permanent_url': None,
                    'storage_location': 'none',
                    'error': 'No image URL provided'
                }
        
        return results
    
    def _generate_s3_key(self, blog_id: str, image_type: str, file_extension: str) -> str:
        """Generate S3 key for media file"""
        date_obj = datetime.now(timezone.utc)
        
        # Create a unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{blog_id}-{image_type}-{unique_id}{file_extension}"
        
        # Organize by date and type
        s3_key = f"{self.media_prefix}/{date_obj.year:04d}/{date_obj.month:02d}/{date_obj.day:02d}/{image_type}/{filename}"
        
        return s3_key
    
    def _get_file_extension(self, url: str, content_type: Optional[str] = None) -> str:
        """Determine file extension from URL or content type"""
        # Try to get extension from URL
        parsed_url = urlparse(url)
        path_ext = os.path.splitext(parsed_url.path)[1]
        
        if path_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return path_ext
        
        # Fallback to content type
        if content_type:
            extension = mimetypes.guess_extension(content_type.split(';')[0])
            if extension:
                return extension
        
        # Default to .png for images
        return '.png'
    
    def create_thumbnail_variants(self, s3_key: str, image_data: Optional[bytes] = None) -> Dict[str, str]:
        """
        Create thumbnail variants of an image
        
        Args:
            s3_key: S3 key of the original image
            image_data: Optional image data to avoid re-downloading
            
        Returns:
            Dict mapping size names to S3 keys
            
        Note: This implementation creates placeholder URLs for thumbnail variants.
        For production use, consider implementing with:
        - PIL/Pillow for local image processing
        - AWS Lambda with image processing libraries
        - Third-party services like Cloudinary or ImageKit
        - S3 + Lambda for serverless thumbnail generation
        """
        try:
            # Parse the original S3 key to create variant keys
            path_parts = s3_key.split('/')
            filename = path_parts[-1]
            name, ext = os.path.splitext(filename)
            dir_path = '/'.join(path_parts[:-1])
            
            # Create variant keys
            variants = {
                'thumbnail_small': f"{dir_path}/{name}_thumb_small{ext}",    # 150x150
                'thumbnail_medium': f"{dir_path}/{name}_thumb_medium{ext}",  # 300x300  
                'thumbnail_large': f"{dir_path}/{name}_thumb_large{ext}",    # 600x600
                'original': s3_key
            }
            
            # For now, return the original URL for all variants
            # TODO: Implement actual image resizing
            logger.info(f"📏 Generated thumbnail variant keys for: {filename}")
            
            # In a full implementation, you would:
            # 1. Download the original image from S3 (if image_data not provided)
            # 2. Use PIL/Pillow to create resized versions
            # 3. Upload each variant to S3 with the generated keys
            # 4. Return the actual URLs
            
            # Example implementation structure:
            # if image_data or self._download_from_s3(s3_key):
            #     from PIL import Image
            #     image = Image.open(BytesIO(image_data))
            #     for size_name, target_key in variants.items():
            #         if size_name != 'original':
            #             resized = self._resize_image(image, size_name)
            #             self._upload_to_s3(target_key, resized)
            
            return variants
            
        except Exception as e:
            logger.error(f"❌ Failed to create thumbnail variants: {str(e)}")
            return {'original': s3_key}
    
    def _resize_image_placeholder(self, size_name: str) -> tuple:
        """
        Placeholder for image resizing logic
        
        Returns appropriate dimensions for each thumbnail size
        """
        size_map = {
            'thumbnail_small': (150, 150),
            'thumbnail_medium': (300, 300), 
            'thumbnail_large': (600, 600)
        }
        return size_map.get(size_name, (300, 300))
    
    def cleanup_temporary_urls(self, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace temporary URLs in blog data with permanent S3 URLs
        
        Args:
            blog_data: Blog post data with potential temporary URLs
            
        Returns:
            Updated blog data with permanent URLs
        """
        if not blog_data.get('media'):
            return blog_data
        
        media = blog_data['media']
        blog_id = blog_data.get('id', str(uuid.uuid4())[:8])
        
        # Collect images to save
        images_to_save = {}
        
        if media.get('featured_image'):
            images_to_save['featured'] = media['featured_image']
        
        if media.get('meme_url') and media['meme_url'] != 'text_only':
            images_to_save['meme'] = media['meme_url']
        
        if media.get('thumbnail_url') and media['thumbnail_url'] != media.get('featured_image'):
            images_to_save['thumbnail'] = media['thumbnail_url']
        
        # Save images to S3
        if images_to_save:
            logger.info(f"💾 Saving {len(images_to_save)} images to S3 for blog {blog_id}")
            storage_results = self.save_multiple_images(images_to_save, blog_id)
            
            # Track URL replacements for content updating
            url_replacements = {}
            
            # Update URLs in blog data
            for image_type, result in storage_results.items():
                if result['success']:
                    if image_type == 'featured':
                        old_url = media['featured_image']
                        media['featured_image'] = result['permanent_url']
                        media['featured_image_s3_key'] = result.get('s3_key')
                        url_replacements[old_url] = result['permanent_url']
                    elif image_type == 'meme':
                        old_url = media['meme_url']
                        media['meme_url'] = result['permanent_url']
                        media['meme_s3_key'] = result.get('s3_key')
                        url_replacements[old_url] = result['permanent_url']
                    elif image_type == 'thumbnail':
                        old_url = media['thumbnail_url']
                        media['thumbnail_url'] = result['permanent_url']
                        media['thumbnail_s3_key'] = result.get('s3_key')
                        url_replacements[old_url] = result['permanent_url']
            
            # Update URLs in content HTML
            if url_replacements and blog_data.get('content'):
                content = blog_data['content']
                for old_url, new_url in url_replacements.items():
                    if old_url in content:
                        content = content.replace(old_url, new_url)
                        logger.info(f"🔗 Replaced URL in content: {old_url[:50]}... -> {new_url[:50]}...")
                blog_data['content'] = content
            
            # Add storage metadata
            media['storage'] = {
                'provider': 's3',
                'bucket': self.bucket_name,
                'saved_at': datetime.now(timezone.utc).isoformat(),
                'results': storage_results
            }
        
        return blog_data
    
    def get_media_stats(self) -> Dict[str, Any]:
        """Get statistics about stored media"""
        if not self.s3_client or not self.bucket_name:
            return {'error': 'S3 not configured'}
        
        try:
            # List objects in media prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{self.media_prefix}/",
                MaxKeys=1000
            )
            
            total_files = response.get('KeyCount', 0)
            total_size = sum(obj.get('Size', 0) for obj in response.get('Contents', []))
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'bucket': self.bucket_name,
                'prefix': self.media_prefix
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting media stats: {str(e)}")
            return {'error': str(e)} 