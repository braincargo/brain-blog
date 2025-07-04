"""
Image Generator - Creates image generation instructions and generates actual images
"""

import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates image instructions and creates actual images using multiple providers with fallbacks"""
    
    def __init__(self, config: Dict[str, Any], providers: Dict[str, Any]):
        self.config = config
        self.providers = providers
        self.image_config = config.get('image_generation', {})
        self.error_config = config.get('error_handling', {})
        self.category_config = config.get('categories', {})
        
        # Provider priority order for fallbacks
        self.provider_priority = ['openai', 'grok', 'gemini']
    
    def generate_instructions(self, blog_post: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Generate detailed image instructions for the blog post"""
        try:
            # Get an available provider for instruction generation
            provider = self._get_available_provider('openai')  # Prefer OpenAI for instructions
            if not provider:
                raise Exception("No LLM providers available for image instruction generation")
            
            # Load image generation prompt
            prompt_content = self._load_prompt('prompts/image_generation/main.txt')
            
            # Build the prompt
            full_prompt = prompt_content.format(
                title=blog_post.get('title', 'Untitled'),
                summary=blog_post.get('summary', ''),
                category=category,
                style_persona=blog_post.get('style_persona', 'Tech Expert')
            )
            
            # Generate instructions using LLM
            result = provider.generate_completion(
                prompt=full_prompt,
                model='creative',
                temperature=0.8,
                max_tokens=500,
                output_format='json'
            )
            
            if result['success']:
                instructions_data = self._parse_instructions_response(result['content'])
                
                return {
                    'success': True,
                    'data': instructions_data,
                    'provider': provider.provider_type,
                    'model': result.get('model', 'unknown')
                }
            else:
                raise Exception(f"Instruction generation failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"❌ Image instruction generation failed: {str(e)}")
            # Fallback to default instructions
            return {
                'success': True,
                'data': self._get_default_instructions(blog_post, category),
                'provider': 'fallback',
                'model': 'default'
            }
    
    def generate_image(self, instructions: Dict[str, Any], blog_post: Dict[str, Any] = None, category: str = "technology") -> Dict[str, Any]:
        """Generate actual image using multiple providers with fallbacks"""
        
        # Get the list of providers to try in order
        providers_to_try = self._get_image_providers_for_category(category)
        
        # Get retry configuration
        max_retries = self.error_config.get('retry_attempts', 3)
        
        last_error = None
        
        for attempt in range(max_retries):
            for provider_name in providers_to_try:
                try:
                    logger.info(f"🎨 Attempting image generation with {provider_name} (attempt {attempt + 1}/{max_retries})")
                    
                    result = self._try_generate_with_provider(provider_name, instructions, blog_post)
                    
                    if result['success']:
                        logger.info(f"✅ Image generated successfully with {provider_name}")
                        return result
                    else:
                        last_error = result.get('error', 'Unknown error')
                        logger.warning(f"⚠️ {provider_name} failed: {last_error}")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"⚠️ {provider_name} failed with exception: {last_error}")
                    continue
        
        # All providers failed
        logger.error(f"❌ All image generation providers failed after {max_retries} attempts. Last error: {last_error}")
        
        # Return a fallback result with placeholder
        return self._get_fallback_image_result(instructions, blog_post, last_error)
    
    def _get_image_providers_for_category(self, category: str) -> List[str]:
        """Get ordered list of providers to try for a specific category"""
        providers_to_try = []
        
        # First, try the category-specific provider if configured
        category_data = self.category_config.get(category, {})
        preferred_provider = category_data.get('image_provider')
        
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
            logger.info(f"📋 Using category-specific image provider for {category}: {preferred_provider}")
        
        # Then try the default image generation provider
        default_provider = self.image_config.get('provider', 'openai')
        if default_provider not in providers_to_try and default_provider in self.providers:
            providers_to_try.append(default_provider)
        
        # Finally, try all other available providers in priority order
        for provider_name in self.provider_priority:
            if provider_name not in providers_to_try and provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_available() and hasattr(provider, 'generate_image'):
                    providers_to_try.append(provider_name)
        
        logger.info(f"🔄 Image generation fallback order: {providers_to_try}")
        return providers_to_try
    
    def _try_generate_with_provider(self, provider_name: str, instructions: Dict[str, Any], blog_post: Dict[str, Any] = None) -> Dict[str, Any]:
        """Try to generate image with a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider or not provider.is_available():
            return {
                'success': False,
                'error': f"{provider_name} provider not available",
                'provider': provider_name
            }
        
        if not hasattr(provider, 'generate_image'):
            return {
                'success': False,
                'error': f"{provider_name} does not support image generation",
                'provider': provider_name
            }
        
        # Build provider-specific prompt
        dalle_prompt = self._build_dalle_prompt(instructions, blog_post)
        
        # Get provider-specific image settings
        size = self._get_provider_image_size(provider_name)
        quality = self._get_provider_image_quality(provider_name)
        
        # Generate image using the provider
        image_result = provider.generate_image(
            prompt=dalle_prompt,
            size=size,
            quality=quality,
            style='natural'
        )
        
        if image_result['success']:
            return {
                'success': True,
                'image_url': image_result['image_url'],
                'thumbnail_url': image_result['image_url'],
                'alt_text': self._generate_alt_text(instructions, blog_post),
                'caption': instructions.get('caption', ''),
                'dalle_prompt': dalle_prompt,
                'revised_prompt': image_result.get('revised_prompt', ''),
                'provider': provider_name,
                'model': image_result.get('model', 'unknown')
            }
        else:
            return {
                'success': False,
                'error': image_result.get('error', 'Unknown error'),
                'provider': provider_name
            }
    
    def _get_provider_image_size(self, provider_name: str) -> str:
        """Get appropriate image size for the provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return self.image_config.get('size', '1792x1024')
        
        # Get the desired size from config
        desired_size = self.image_config.get('size', '1792x1024')
        
        # Check if provider supports this size
        if hasattr(provider, 'validate_size'):
            return provider.validate_size(desired_size)
        
        # Fallback for providers without size validation
        supported_sizes = getattr(provider, 'supported_sizes', ['1024x1024'])
        if desired_size in supported_sizes:
            return desired_size
        
        # Use provider's default size
        return getattr(provider, 'default_size', '1024x1024')
    
    def _get_provider_image_quality(self, provider_name: str) -> str:
        """Get appropriate image quality for the provider"""
        # OpenAI supports 'hd' and 'standard'
        if provider_name == 'openai':
            return self.image_config.get('quality', 'hd')
        
        # Other providers typically use 'standard'
        return 'standard'
    
    def _get_fallback_image_result(self, instructions: Dict[str, Any], blog_post: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Generate a fallback result when all providers fail"""
        return {
            'success': False,
            'error': f"All image generation providers failed: {error}",
            'image_url': None,
            'thumbnail_url': None,
            'alt_text': self._generate_alt_text(instructions, blog_post),
            'caption': instructions.get('caption', ''),
            'dalle_prompt': self._build_dalle_prompt(instructions, blog_post),
            'provider': 'none',
            'fallback_used': True
        }

    def _get_available_provider(self, preferred: str = None) -> Any:
        """Get an available provider, preferring the specified one"""
        if preferred and preferred in self.providers:
            provider = self.providers[preferred]
            if provider.is_available():
                return provider
        
        # Fallback to any available provider
        for provider in self.providers.values():
            if provider.is_available():
                return provider
        
        return None
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt template from file"""
        try:
            # Handle relative paths - ensure we're looking from the project root
            if not os.path.isabs(prompt_file):
                # Get the directory where this script is located
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up one level to project root, then find the prompt file
                project_root = os.path.dirname(script_dir)
                prompt_file = os.path.join(project_root, prompt_file)
            
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r') as f:
                    return f.read().strip()
            else:
                logger.warning(f"Prompt file not found: {prompt_file}")
                return self._get_default_prompt()
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_file}: {str(e)}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default image instruction prompt"""
        return """Create detailed instructions for generating a professional blog featured image.

Blog Details:
- Title: {title}
- Summary: {summary}
- Category: {category}
- Style: {style_persona}

Generate JSON with these fields:
{{
  "prompt": "Detailed DALL-E prompt for image generation",
  "style": "Visual style description",
  "composition": "Layout and composition details",
  "colors": "Color palette and scheme",
  "mood": "Emotional tone of the image",
  "caption": "Image caption for the blog"
}}"""
    
    def _parse_instructions_response(self, response_content: str) -> Dict[str, Any]:
        """Parse the LLM response into structured instructions"""
        try:
            import json
            import re
            
            # Clean up the response
            cleaned_content = response_content.strip()
            
            # Try to parse as JSON
            if cleaned_content.startswith('{') and cleaned_content.endswith('}'):
                return json.loads(cleaned_content)
            
            # Try to extract JSON from code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1).strip())
            
            # Look for JSON-like content
            json_start = cleaned_content.find('{')
            json_end = cleaned_content.rfind('}')
            if json_start >= 0 and json_end > json_start:
                json_content = cleaned_content[json_start:json_end+1]
                return json.loads(json_content)
            
            # Fallback to default
            return self._get_default_instructions_data()
            
        except Exception as e:
            logger.error(f"Error parsing instructions response: {str(e)}")
            return self._get_default_instructions_data()
    
    def _get_default_instructions(self, blog_post: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Get default image instructions"""
        return {
            'prompt': f'Professional featured image for blog post about {blog_post.get("title", "technology")}',
            'style': 'Clean, modern, professional',
            'composition': 'Centered with subtle tech elements',
            'colors': 'Gold accent (#DDBC74) with modern palette',
            'mood': 'Innovative and empowering',
            'caption': f'Featured image for "{blog_post.get("title", "Blog Post")}"'
        }
    
    def _get_default_instructions_data(self) -> Dict[str, Any]:
        """Get default instructions data structure"""
        return {
            'prompt': 'Professional technology blog featured image with modern design',
            'style': 'Clean, modern, professional',
            'composition': 'Centered composition',
            'colors': 'Modern palette with gold accents',
            'mood': 'Professional and engaging',
            'caption': 'Blog featured image'
        }
    
    def _build_dalle_prompt(self, instructions: Dict[str, Any], blog_post: Dict[str, Any] = None) -> str:
        """Build optimized DALL-E prompt from instructions"""
        base_prompt = instructions.get('prompt', 'Professional blog featured image')
        
        # Enhance prompt with DALL-E best practices
        enhanced_prompt = f"{base_prompt}, "
        
        # Add style elements
        if 'style' in instructions:
            enhanced_prompt += f"{instructions['style']}, "
        
        if 'composition' in instructions:
            enhanced_prompt += f"{instructions['composition']}, "
        
        if 'colors' in instructions:
            enhanced_prompt += f"{instructions['colors']}, "
        
        if 'mood' in instructions:
            enhanced_prompt += f"{instructions['mood']} mood, "
        
        # Add technical specifications
        enhanced_prompt += "high quality, professional photography style, sharp focus, well-lit"
        
        # Limit prompt length for DALL-E
        if len(enhanced_prompt) > 400:
            enhanced_prompt = enhanced_prompt[:400] + "..."
        
        return enhanced_prompt
    
    def _generate_alt_text(self, instructions: Dict[str, Any], blog_post: Dict[str, Any] = None) -> str:
        """Generate accessibility alt text for the image"""
        title = blog_post.get('title', 'blog post') if blog_post else 'blog post'
        style = instructions.get('style', 'professional')
        
        return f"Featured image for {title} - {style} design" 