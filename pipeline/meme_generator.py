"""
Meme Generator - Creates witty tech memes with actual meme creation
"""

import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MemeGenerator:
    """Generates witty tech memes for blog posts"""
    
    def __init__(self, config: Dict[str, Any], providers: Dict[str, Any]):
        self.config = config
        self.providers = providers
        self.meme_config = config.get('meme_generation', {})
        self.error_config = config.get('error_handling', {})
        self.category_config = config.get('categories', {})
        self.meme_templates = self.meme_config.get('templates', [
            'drake_pointing', 'distracted_boyfriend', 'expanding_brain', 
            'this_is_fine', 'change_my_mind'
        ])
        
        # Provider priority order for fallbacks
        self.provider_priority = ['openai', 'grok', 'gemini']
    
    def generate(self, blog_post: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Generate meme for the blog post"""
        try:
            # Get an available provider for meme text generation
            provider = self._get_available_provider('openai')  # Prefer OpenAI for creativity
            if not provider:
                raise Exception("No LLM providers available for meme generation")
            
            # Load meme generation prompt
            prompt_content = self._load_prompt('prompts/meme_generation/main.txt')
            
            # Build the prompt
            full_prompt = prompt_content.format(
                title=blog_post.get('title', 'Untitled'),
                summary=blog_post.get('summary', ''),
                category=category,
                style_persona=blog_post.get('style_persona', 'Tech Expert')
            )
            
            # Generate meme content using LLM
            result = provider.generate_completion(
                prompt=full_prompt,
                model='creative',
                temperature=0.9,  # Higher temperature for more creative memes
                max_tokens=300,
                output_format='json'
            )
            
            if result['success']:
                meme_data = self._parse_meme_response(result['content'])
                
                # Generate the actual meme image with fallbacks
                meme_image = self._create_meme_image_with_fallbacks(meme_data, blog_post, category)
                
                return {
                    'success': True,
                    'data': {
                        **meme_data,
                        **meme_image
                    },
                    'provider': provider.provider_type,
                    'model': result.get('model', 'unknown')
                }
            else:
                raise Exception(f"Meme generation failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"❌ Meme generation failed: {str(e)}")
            # Fallback to default meme
            return {
                'success': True,
                'data': self._get_default_meme(blog_post, category),
                'provider': 'fallback',
                'model': 'default'
            }
    
    def _create_meme_image_with_fallbacks(self, meme_data: Dict[str, Any], blog_post: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Create meme image using multiple providers with fallbacks"""
        
        # Get the list of providers to try in order
        providers_to_try = self._get_meme_providers_for_category(category)
        
        # Get retry configuration
        max_retries = self.error_config.get('retry_attempts', 3)
        
        last_error = None
        
        for attempt in range(max_retries):
            for provider_name in providers_to_try:
                try:
                    logger.info(f"🎭 Attempting meme image generation with {provider_name} (attempt {attempt + 1}/{max_retries})")
                    
                    result = self._try_generate_meme_with_provider(provider_name, meme_data, blog_post)
                    
                    if result['success']:
                        logger.info(f"✅ Meme image generated successfully with {provider_name}")
                        return result
                    else:
                        last_error = result.get('error', 'Unknown error')
                        logger.warning(f"⚠️ Meme image generation failed with {provider_name}: {last_error}")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"⚠️ {provider_name} meme generation failed with exception: {last_error}")
                    continue
        
        # All providers failed, fall back to text-only meme
        logger.warning(f"⚠️ All meme image providers failed after {max_retries} attempts. Using text-only meme. Last error: {last_error}")
        
        return {
            'meme_url': 'text_only',
            'meme_type': 'text_only',
            'alt_text': f"Meme: {meme_data.get('top_text', '')} / {meme_data.get('bottom_text', '')}",
            'meme_description': meme_data.get('context', 'Tech meme'),
            'fallback_used': True,
            'error': last_error
        }
    
    def _get_meme_providers_for_category(self, category: str) -> List[str]:
        """Get ordered list of providers to try for meme generation in a specific category"""
        providers_to_try = []
        
        # First, try the category-specific meme provider if configured
        category_data = self.category_config.get(category, {})
        preferred_provider = category_data.get('meme_provider')
        
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
            logger.info(f"📋 Using category-specific meme provider for {category}: {preferred_provider}")
        
        # Then try the default meme generation provider
        default_provider = self.meme_config.get('provider', 'openai')
        if default_provider not in providers_to_try and default_provider in self.providers:
            providers_to_try.append(default_provider)
        
        # Finally, try all other available providers in priority order
        for provider_name in self.provider_priority:
            if provider_name not in providers_to_try and provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_available() and hasattr(provider, 'generate_image'):
                    providers_to_try.append(provider_name)
        
        logger.info(f"🔄 Meme generation fallback order: {providers_to_try}")
        return providers_to_try
    
    def _try_generate_meme_with_provider(self, provider_name: str, meme_data: Dict[str, Any], blog_post: Dict[str, Any]) -> Dict[str, Any]:
        """Try to generate meme image with a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider or not provider.is_available():
            return {
                'success': False,
                'error': f"{provider_name} provider not available"
            }
        
        if not hasattr(provider, 'generate_image'):
            return {
                'success': False,
                'error': f"{provider_name} does not support image generation"
            }
        
        # Build meme prompt for the provider
        meme_prompt = self._build_meme_dalle_prompt(meme_data, blog_post)
        
        # Generate meme image using the provider
        image_result = provider.generate_image(
            prompt=meme_prompt,
            size='1024x1024',  # Square format for memes
            quality='standard',  # Standard quality for memes
            style='natural'
        )
        
        if image_result['success']:
            return {
                'success': True,
                'meme_url': image_result['image_url'],
                'meme_type': 'generated_image',
                'alt_text': f"Meme about {blog_post.get('title', 'technology')}: {meme_data.get('context', '')}",
                'meme_description': meme_data.get('context', 'Tech meme'),
                'dalle_prompt': meme_prompt,
                'revised_prompt': image_result.get('revised_prompt', ''),
                'provider': provider_name,
                'model': image_result.get('model', 'unknown')
            }
        else:
            return {
                'success': False,
                'error': image_result.get('error', 'Unknown error')
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
        """Default meme generation prompt"""
        return """Create a witty tech meme for this blog post.

Blog Details:
- Title: {title}
- Summary: {summary}
- Category: {category}
- Style: {style_persona}

Available meme templates: {available_templates}

Generate JSON with these fields:
{{
  "template": "best_template_for_this_content",
  "top_text": "Short, punchy text for top",
  "bottom_text": "Short, punchy text for bottom",
  "context": "Brief explanation of the meme concept",
  "humor_type": "type of humor (comparison, irony, etc.)"
}}"""
    
    def _parse_meme_response(self, response_content: str) -> Dict[str, Any]:
        """Parse the LLM response into structured meme data"""
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
            return self._get_default_meme_data()
            
        except Exception as e:
            logger.error(f"Error parsing meme response: {str(e)}")
            return self._get_default_meme_data()
    
    def _create_meme_image(self, meme_data: Dict[str, Any], blog_post: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - now uses fallback system"""
        return self._create_meme_image_with_fallbacks(meme_data, blog_post, "technology")
    
    def _build_meme_dalle_prompt(self, meme_data: Dict[str, Any], blog_post: Dict[str, Any]) -> str:
        """Build DALL-E prompt for meme generation"""
        template = meme_data.get('template', 'drake_pointing')
        top_text = meme_data.get('top_text', '')
        bottom_text = meme_data.get('bottom_text', '')
        
        # Template-specific prompts
        template_prompts = {
            'drake_pointing': f"Drake pointing meme format: Drake rejecting '{top_text}' in top panel, Drake approving '{bottom_text}' in bottom panel, clear text overlay, meme style",
            'distracted_boyfriend': f"Distracted boyfriend meme: man labeled '{top_text}' looking at woman labeled '{bottom_text}', girlfriend in background, meme format",
            'expanding_brain': f"Expanding brain meme: progressive panels showing evolution from '{top_text}' to '{bottom_text}', glowing brain, meme style",
            'this_is_fine': f"This is fine meme: character in burning room saying '{top_text}' while '{bottom_text}' happens around them, meme format",
            'change_my_mind': f"Change my mind meme: person at table with sign saying '{top_text}' and '{bottom_text}', college campus setting, meme style"
        }
        
        base_prompt = template_prompts.get(template, f"Internet meme style image with text '{top_text}' and '{bottom_text}', popular meme format")
        
        # Add meme-specific styling
        full_prompt = f"{base_prompt}, internet meme style, bold text overlay, high contrast, clear readable text, popular social media meme format"
        
        # Limit prompt length
        if len(full_prompt) > 400:
            full_prompt = full_prompt[:400] + "..."
        
        return full_prompt
    
    def _get_default_meme(self, blog_post: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Get default meme data"""
        title = blog_post.get('title', 'Technology')
        
        return {
            'template': 'drake_pointing',
            'top_text': 'Old tech approaches',
            'bottom_text': 'BrainCargo solutions',
            'context': f'Meme about {title}',
            'humor_type': 'comparison',
            'meme_url': 'text_only',  # Flag for text-only meme rendering
            'meme_type': 'text_only',
            'alt_text': f"Meme: Old tech approaches / BrainCargo solutions",
            'meme_description': f'Comparison meme about {title}'
        }
    
    def _get_default_meme_data(self) -> Dict[str, Any]:
        """Get default meme data structure"""
        return {
            'template': 'drake_pointing',
            'top_text': 'Centralized AI',
            'bottom_text': 'Own Your AI',
            'context': 'Comparison meme about AI ownership',
            'humor_type': 'comparison'
        } 