"""
Gemini Provider Implementation (Google)
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from .base import MultiModalProvider

logger = logging.getLogger(__name__)


class GeminiProvider(MultiModalProvider):
    """Gemini provider implementation for Google"""
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if not GENAI_AVAILABLE:
                logger.error("❌ google-genai package not installed. Install with: pip install google-genai")
                return
            
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                logger.error(f"❌ {self.api_key_env} environment variable not found")
                return
            
            # Configure the GenAI client
            self.client = genai.Client(api_key=api_key)
            self.api_key = api_key
            
            logger.info("✅ Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Gemini client initialization failed: {str(e)}")
    
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
        """Generate completion using Gemini API"""
        if not self.is_available():
            raise Exception("Gemini provider not available")
        
        model_name = self.get_model_name(model)
        temp = self.get_temperature(temperature)
        max_tok = self.get_max_tokens(max_tokens)
        
        try:
            # Build the prompt with system prompt if provided
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            else:
                full_prompt = prompt
            
            # Generate content using the new genai client
            response = self.client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            
            # Extract content from response
            if response and response.text:
                return {
                    'content': response.text,
                    'provider': 'gemini',
                    'model': model_name,
                    'output_format': output_format,
                    'success': True,
                    'usage': getattr(response, 'usage_metadata', {})
                }
            else:
                raise Exception("No content in Gemini response")
            
        except Exception as e:
            logger.error(f"❌ Gemini completion failed: {str(e)}")
            return {
                'content': None,
                'provider': 'gemini',
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
        """Generate image using Gemini - Currently not supported with genai client"""
        logger.warning("⚠️ Image generation not yet supported with google-genai client")
        return {
            'image_url': None,
            'error': 'Image generation not yet supported with google-genai client',
            'provider': 'gemini',
            'success': False
        }
    

    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        if not GENAI_AVAILABLE:
            return False
            
        if not hasattr(self, 'client') or not self.client:
            return False
            
        if not hasattr(self, 'api_key') or not self.api_key:
            return False
        
        try:
            # Test API connectivity with a simple request
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Test"
            )
            return bool(response and response.text)
            
        except Exception as e:
            logger.error(f"❌ Gemini availability check failed: {str(e)}")
            return False 