"""
Anthropic Provider Implementation
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider implementation"""
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client"""
        try:
            from anthropic import Anthropic
            
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                logger.error(f"❌ {self.api_key_env} environment variable not found")
                return
                
            self.client = Anthropic(api_key=api_key)
            logger.info("✅ Anthropic client initialized successfully")
            
        except ImportError:
            logger.error("❌ Anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"❌ Anthropic client initialization failed: {str(e)}")
    
    def generate_completion(
        self,
        prompt: str,
        model: str = "standard",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        output_format: str = "text",
        system_prompt: Optional[str] = None,
        use_knowledge_files: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate completion using Anthropic API
        
        Args:
            prompt: The input prompt
            model: Model type (fast, standard, creative)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            output_format: Expected format (text, json)
            system_prompt: System prompt for completion
            use_knowledge_files: Whether to include uploaded knowledge files
            **kwargs: Additional parameters
            
        Returns:
            Dict with completion results
        """
        if not self.is_available():
            raise Exception("Anthropic provider not available")
        
        model_name = self.get_model_name(model)
        temp = self.get_temperature(temperature)
        max_tok = self.get_max_tokens(max_tokens)
        
        try:
            # Prepare message content
            content_parts = [{"type": "text", "text": prompt}]
            
            # Add knowledge files if requested
            if use_knowledge_files:
                file_ids = self._get_knowledge_file_ids()
                if file_ids:
                    logger.info(f"📚 Using {len(file_ids)} Anthropic knowledge files")
                    for file_id in file_ids:
                        content_parts.append({
                            "type": "document",
                            "source": {
                                "type": "file",
                                "file_id": file_id
                            }
                        })
                else:
                    logger.warning("⚠️ No Anthropic knowledge files found. Run 'make vector-upload-anthropic' to upload files.")
            
            # Prepare messages
            messages = [{"role": "user", "content": content_parts}]
            
            # Prepare extra headers for Files API if using knowledge files
            extra_headers = {}
            if use_knowledge_files and file_ids:
                extra_headers["anthropic-beta"] = "files-api-2025-04-14"
            
            # Create completion
            response = self.client.messages.create(
                model=model_name,
                max_tokens=max_tok,
                temperature=temp,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=messages,
                extra_headers=extra_headers
            )
            
            content = response.content[0].text if response.content else ""
            
            return {
                'content': content,
                'provider': 'anthropic',
                'model': model_name,
                'output_format': output_format,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic completion failed: {str(e)}")
            return {
                'content': None,
                'provider': 'anthropic',
                'model': model_name,
                'error': str(e),
                'success': False
            }
    
    def _get_knowledge_file_ids(self) -> list:
        """Get uploaded file IDs from manifest"""
        # First check environment variable
        env_files = os.environ.get('ANTHROPIC_FILE_IDS')
        if env_files:
            return env_files.split(',')
        
        # Then check configuration
        config_files = self.config.get('file_ids', [])
        if config_files:
            return config_files if isinstance(config_files, list) else [config_files]
        
        # Finally check manifest file
        manifest_path = "openai_store/anthropic_uploads.json"
        try:
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    uploaded_files = manifest.get('uploaded_files', [])
                    return [file_info.get('id') for file_info in uploaded_files if file_info.get('id')]
        except Exception as e:
            logger.warning(f"⚠️ Could not read Anthropic uploads manifest: {e}")
            
        return []
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        if not self.client:
            return False
            
        try:
            # Simple availability check would require a test call
            # For now, just check if client exists
            return True
        except Exception as e:
            logger.error(f"❌ Anthropic availability check failed: {str(e)}")
            return False
    
    def generate_image(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Anthropic doesn't support image generation
        """
        return {
            'image_url': None,
            'error': 'Image generation not supported by Anthropic',
            'provider': 'anthropic',
            'success': False
        } 