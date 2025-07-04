"""
Grok Provider Implementation (xAI)
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional

from .base import MultiModalProvider

logger = logging.getLogger(__name__)


class GrokProvider(MultiModalProvider):
    """Grok provider implementation for xAI"""
    
    def _initialize_client(self):
        """Initialize Grok client"""
        try:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                logger.error(f"❌ {self.api_key_env} environment variable not found")
                return
            
            # Grok uses API key authentication
            self.api_key = api_key
            self.base_url = "https://api.x.ai/v1"
            logger.info("✅ Grok client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Grok client initialization failed: {str(e)}")
    
    def generate_completion(
        self,
        prompt: str,
        model: str = "standard",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        output_format: str = "text",
        system_prompt: Optional[str] = None,
        use_responses_api: bool = False,
        use_knowledge_files: bool = False,
        tools: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Grok API"""
        if not self.is_available():
            raise Exception("Grok provider not available")
        
        model_name = self.get_model_name(model)
        temp = self.get_temperature(temperature)
        max_tok = self.get_max_tokens(max_tokens)
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temp,
                "max_tokens": max_tok
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return {
                'content': content,
                'provider': 'grok',
                'model': model_name,
                'output_format': output_format,
                'success': True,
                'usage': result.get('usage', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Grok completion failed: {str(e)}")
            return {
                'content': None,
                'provider': 'grok',
                'model': model_name,
                'error': str(e),
                'success': False
            }
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using Grok's image generation API"""
        if not self.is_available():
            raise Exception("Grok provider not available")
        
        try:
            # Validate size
            validated_size = self.validate_size(size)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Grok image generation payload
            payload = {
                "model": self.get_image_model_name(),
                "prompt": prompt,
                "size": validated_size,
                "quality": quality,
                "style": style,
                "n": 1
            }
            
            logger.info(f"🎨 Generating image with Grok: {prompt[:100]}...")
            
            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=120  # Image generation takes longer
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('data') and len(result['data']) > 0:
                image_data = result['data'][0]
                logger.info("✅ Grok image generated successfully")
                
                return {
                    'image_url': image_data['url'],
                    'revised_prompt': image_data.get('revised_prompt', prompt),
                    'provider': 'grok',
                    'model': self.get_image_model_name(),
                    'size': validated_size,
                    'quality': quality,
                    'style': style,
                    'success': True
                }
            else:
                raise Exception("No image data received from Grok")
                
        except Exception as e:
            logger.error(f"❌ Grok image generation failed: {str(e)}")
            return {
                'image_url': None,
                'error': str(e),
                'provider': 'grok',
                'success': False
            }
    
    def is_available(self) -> bool:
        """Check if Grok is available"""
        if not hasattr(self, 'api_key') or not self.api_key:
            return False
        
        try:
            # Test API connectivity
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ Grok availability check failed: {str(e)}")
            return False 