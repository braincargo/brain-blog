"""
OpenAI Provider Implementation
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from .base import MultiModalProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(MultiModalProvider):
    """OpenAI provider implementation"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                logger.error(f"❌ {self.api_key_env} environment variable not found")
                return
                
            self.client = OpenAI(api_key=api_key)
            logger.info("✅ OpenAI client initialized successfully")
            
        except ImportError:
            logger.error("❌ OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"❌ OpenAI client initialization failed: {str(e)}")
    
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
        """
        Generate completion using OpenAI API
        
        Args:
            prompt: The input prompt
            model: Model type (fast, standard, creative)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            output_format: Expected format (text, json)
            system_prompt: System prompt for chat completion
            use_responses_api: Whether to use Responses API
            tools: Tools for function calling
            **kwargs: Additional parameters
            
        Returns:
            Dict with completion results
        """
        if not self.is_available():
            raise Exception("OpenAI provider not available")
        
        model_name = self.get_model_name(model)
        temp = self.get_temperature(temperature)
        max_tok = self.get_max_tokens(max_tokens)
        
        # Log which model is actually being used
        logger.info(f"🤖 OpenAI using model: {model_name} (requested: {model})")
        
        try:
            import time
            start_time = time.time()
            logger.info(f"⏱️ Starting OpenAI API call at {time.strftime('%H:%M:%S')}")
            
            # Add vector store tools if knowledge files are requested
            enhanced_tools = tools or []
            if use_knowledge_files:
                enhanced_tools = self._add_vector_store_tools(enhanced_tools)
                logger.info("📚 Using OpenAI vector store for BrainCargo knowledge")
            
            # Check if this model requires Responses API (o3, o1 series)
            if self._is_responses_model(model_name):
                # Force Responses API for o3-pro, o1, etc.
                if not system_prompt:
                    system_prompt = "You are a helpful AI assistant."
                response = self._generate_with_responses_api(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model_name,
                    temperature=temp,
                    max_tokens=max_tok,
                    tools=enhanced_tools,
                    **kwargs
                )
            elif self._is_completion_model(model_name):
                # Use Completion API for legacy models
                response = self._generate_with_completion_api(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model_name,
                    temperature=temp,
                    max_tokens=max_tok,
                    **kwargs
                )
            elif use_responses_api and system_prompt:
                # Use newer Responses API
                response = self._generate_with_responses_api(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model_name,
                    temperature=temp,
                    max_tokens=max_tok,
                    tools=enhanced_tools,
                    **kwargs
                )
            else:
                # Use traditional Chat Completion API
                response = self._generate_with_chat_completion(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model_name,
                    temperature=temp,
                    max_tokens=max_tok,
                    tools=enhanced_tools,
                    **kwargs
                )
            
            # Log completion timing
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"⏱️ OpenAI API call completed in {duration:.2f} seconds")
            
            return {
                'content': response,
                'provider': 'openai',
                'model': model_name,
                'output_format': output_format,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI completion failed: {str(e)}")
            return {
                'content': None,
                'provider': 'openai',
                'model': model_name,
                'error': str(e),
                'success': False
            }
    
    def _generate_with_responses_api(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[list] = None,
        **kwargs
    ) -> str:
        """Generate using OpenAI Responses API"""
        
        # Prepare tools
        api_tools = []
        if tools:
            for tool in tools:
                if tool.get("type") == "web_search":
                    api_tools.append({"type": "web_search"})
                elif tool.get("type") == "file_search" and tool.get("vector_store_ids"):
                    api_tools.append({
                        "type": "file_search",
                        "vector_store_ids": tool["vector_store_ids"]
                    })
        
        # Create response with minimal parameters for o3-pro
        response_kwargs = {
            "model": model,
            "instructions": system_prompt,
            "input": prompt
        }
        
        # Add tools if available
        if api_tools:
            response_kwargs["tools"] = api_tools
        
        response = self.client.responses.create(**response_kwargs)
        
        return response.output_text
    
    def _is_completion_model(self, model: str) -> bool:
        """Check if model uses completion API instead of chat API"""
        completion_models = [
            "text-davinci-003", "text-davinci-002", 
            "davinci", "curie", "babbage", "ada"
        ]
        return any(comp_model in model for comp_model in completion_models)
    
    def _is_responses_model(self, model: str) -> bool:
        """Check if model requires Responses API"""
        responses_models = [
            "o3-pro", "o3-mini", "o3", "o1", "o1-mini", "o1-preview"
        ]
        return any(resp_model in model for resp_model in responses_models)
    
    def _generate_with_completion_api(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI Completion API (for o3-pro and similar models)"""
        
        # Combine system prompt and user prompt for completion models
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        completion_kwargs = {
            "model": model,
            "prompt": full_prompt,
            "max_tokens": max_tokens,
        }
        
        # o3 models only support temperature=1 (default), so don't set it
        if "o3" not in model:
            completion_kwargs["temperature"] = temperature
        
        response = self.client.completions.create(**completion_kwargs)
        
        return response.choices[0].text.strip()
    
    def _generate_with_chat_completion(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[list] = None,
        **kwargs
    ) -> str:
        """Generate using OpenAI Chat Completion API"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare tools for chat completion
        api_tools = []
        if tools:
            for tool in tools:
                if tool.get("type") == "file_search" and tool.get("vector_store_ids"):
                    api_tools.append({
                        "type": "file_search",
                        "vector_store_ids": tool["vector_store_ids"]
                    })
        
        completion_kwargs = {
            "model": model,
            "messages": messages
        }
        
        # o3 models only support temperature=1 (default)
        if "o3" not in model and "o1" not in model:
            completion_kwargs["temperature"] = temperature
        
        # Use correct token parameter based on model
        if "o1" in model or "o3" in model:
            completion_kwargs["max_completion_tokens"] = max_tokens
        else:
            completion_kwargs["max_tokens"] = max_tokens
        
        if api_tools:
            completion_kwargs["tools"] = api_tools
        
        response = self.client.chat.completions.create(**completion_kwargs)
        
        return response.choices[0].message.content
    
    def _add_vector_store_tools(self, existing_tools: list) -> list:
        """Add BrainCargo vector store tools for knowledge file access"""
        # Load vector store ID from manifest file
        vector_store_id = self._get_vector_store_id()
        
        if not vector_store_id:
            logger.warning("⚠️ No OpenAI vector store ID found. Run 'make vector-upload-openai' to create one.")
            return existing_tools
        
        # Add file search tool with BrainCargo vector store
        vector_store_tool = {
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }
        
        # Check if file_search tool already exists
        has_file_search = any(tool.get("type") == "file_search" for tool in existing_tools)
        
        if not has_file_search:
            existing_tools.append(vector_store_tool)
            logger.info(f"📚 Added vector store {vector_store_id} to tools")
        
        return existing_tools
    
    def _get_vector_store_id(self) -> Optional[str]:
        """Get vector store ID from manifest file or environment"""
        # First check environment variable
        env_ids = os.environ.get('OPENAI_VECTOR_STORE_IDS')
        if env_ids:
            # Return first ID if multiple provided
            return env_ids.split(',')[0].strip()
            
        # Then check configuration
        config_ids = self.config.get('vector_store_ids')
        if config_ids:
            if isinstance(config_ids, list):
                return config_ids[0]
            return str(config_ids).split(',')[0].strip()
        
        # Finally check manifest file
        manifest_path = "openai_store/openai_vector_store.json"
        try:
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    return manifest.get('vector_store_id')
        except Exception as e:
            logger.warning(f"⚠️ Could not read vector store manifest: {e}")
            
        return None
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        if not self.client:
            return False
            
        try:
            # Simple test call
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"❌ OpenAI availability check failed: {str(e)}")
            return False
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1792x1024",
        quality: str = "hd",
        style: str = "natural",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using DALL-E
        
        Args:
            prompt: Image generation prompt
            size: Image size
            quality: Image quality
            style: Image style
            
        Returns:
            Dict with image URL and metadata
        """
        if not self.is_available():
            raise Exception("OpenAI provider not available")
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            return {
                'image_url': response.data[0].url,
                'revised_prompt': response.data[0].revised_prompt,
                'provider': 'openai',
                'model': 'dall-e-3',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI image generation failed: {str(e)}")
            return {
                'image_url': None,
                'error': str(e),
                'provider': 'openai',
                'success': False
            } 