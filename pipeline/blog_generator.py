"""
Blog Generator - Generates blog posts using category-specific styles
"""

import logging
import os
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BlogGenerator:
    """Generates blog posts with category-specific styling"""
    
    def __init__(self, config: Dict[str, Any], providers: Dict[str, Any]):
        self.config = config
        self.providers = providers
        self.categories_config = config.get('categories', {})
    
    def generate(self, url: str, content: str, category: str, custom_title: str = "", categorization_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate blog post with category-specific styling
        """
        try:
            # Get category configuration
            category_config = self.categories_config.get(category, {})
            if not category_config:
                logger.warning(f"No configuration found for category: {category}")
                category_config = self.categories_config.get('technology', {})  # Fallback
            
            # Determine provider and model
            provider_name = category_config.get('provider_override', 'openai')
            provider = self.providers.get(provider_name)
            
            if not provider or not provider.is_available():
                logger.warning(f"Provider {provider_name} not available, falling back to first available")
                provider = next((p for p in self.providers.values() if p.is_available()), None)
                if not provider:
                    raise Exception("No LLM providers available")
                provider_name = provider.provider_type
            
            # Load prompts
            base_prompt = self._load_prompt('prompts/blog_generation/base.txt')
            style_prompt_file = category_config.get('style_prompt', 'blog_generation/tech_style.txt')
            # Add prompts/ prefix if not already present
            if not style_prompt_file.startswith('prompts/'):
                style_prompt_file = f'prompts/{style_prompt_file}'
            style_prompt = self._load_prompt(style_prompt_file)
            
            # Build final prompt
            final_prompt = self._build_blog_prompt(
                base_prompt=base_prompt,
                style_prompt=style_prompt,
                url=url,
                content=content,
                category=category,
                custom_title=custom_title,
                style_persona=category_config.get('style_persona', 'Tech Expert')
            )
            
            # Generate blog post using the provider
            # Use knowledge files if provider is Anthropic
            use_knowledge = provider.provider_type == 'anthropic'
            
            result = provider.generate_completion(
                prompt=final_prompt,
                model='standard',
                temperature=0.7,
                max_tokens=3000,
                output_format='json',
                use_knowledge_files=use_knowledge
            )
            
            if not result['success']:
                raise Exception(f"Blog generation failed: {result.get('error', 'Unknown error')}")
            
            # Parse the blog post data
            blog_data = self._parse_blog_response(result['content'], category, category_config)
            
            logger.info(f"✅ Blog post generated successfully using {provider_name}")
            
            return {
                'success': True,
                'data': blog_data,
                'provider': provider_name,
                'model': result.get('model', 'unknown'),
                'usage': result.get('usage', {}),
                'needs_media': True  # Flag to indicate this needs image/meme generation
            }
            
        except Exception as e:
            logger.error(f"❌ Blog generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
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
                return "Generate a professional blog post about the given content."
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_file}: {str(e)}")
            return "Generate a professional blog post about the given content."
    
    def _build_blog_prompt(self, base_prompt: str, style_prompt: str, url: str, content: str, 
                          category: str, custom_title: str, style_persona: str) -> str:
        """Build the complete blog generation prompt"""
        
        # Extract original title from content if available
        original_title = self._extract_title_from_content(content) or "No original title available"
        
        # Check if style prompt has variables to format
        style_instructions = style_prompt
        if '{' in style_prompt and '}' in style_prompt:
            try:
                # Only format if template has variables
                style_instructions = style_prompt.format(
                    url=url,
                    content=content[:2000],
                    category=category,
                    style_persona=style_persona
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Style prompt formatting failed: {str(e)}, using template as-is")
                style_instructions = style_prompt
        
        # Format the base prompt with variables
        try:
            formatted_base = base_prompt.format(
                url=url,
                original_title=original_title,
                content=content[:2000],  # Limit content length
                category=category,
                style_persona=style_persona,
                style_instructions=style_instructions
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Base prompt formatting failed: {str(e)}")
            # Fallback: create a simple prompt
            formatted_base = f"""Write a blog post about the content from {url}.
            
Category: {category}
Style: {style_persona}
Content: {content[:1000]}

{style_instructions}

Respond with valid JSON format."""
        
        return formatted_base
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from content if available"""
        # Simple title extraction - look for first line or HTML title
        lines = content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # Remove common HTML tags if present
            import re
            clean_title = re.sub(r'<[^>]+>', '', first_line).strip()
            if clean_title and len(clean_title) < 200:  # Reasonable title length
                return clean_title
        return ""
    
    def _parse_blog_response(self, response_content: str, category: str, category_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the LLM response into structured blog data"""
        try:
            # Clean up the response content
            cleaned_content = response_content.strip()
            
            # Try to parse as JSON first
            if cleaned_content.startswith('{') and cleaned_content.endswith('}'):
                blog_data = json.loads(cleaned_content)
            else:
                # If not JSON, try to extract JSON from code blocks
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                    blog_data = json.loads(json_content)
                else:
                    # Look for JSON-like content in the response
                    json_start = cleaned_content.find('{')
                    json_end = cleaned_content.rfind('}')
                    if json_start >= 0 and json_end > json_start:
                        json_content = cleaned_content[json_start:json_end+1]
                        try:
                            blog_data = json.loads(json_content)
                        except json.JSONDecodeError:
                            # Fallback: create structured data from plain text
                            blog_data = {
                                'title': 'BrainCargo Blog Post',
                                'summary': 'BrainCargo summary of the content.',
                                'content': cleaned_content
                            }
                    else:
                        # Fallback: create structured data from plain text
                        blog_data = {
                            'title': 'BrainCargo Blog Post',
                            'summary': 'BrainCargo summary of the content.',
                            'content': cleaned_content
                        }
            
            # Ensure required fields
            blog_data.setdefault('category', category)
            blog_data.setdefault('style_persona', category_config.get('style_persona', 'Tech Expert'))
            
            # Add key elements (customizable via environment)
            blog_data['key_elements'] = [
                'user sovereignty',
                'AI ownership', 
                'privacy protection',
                'fair compensation'
            ]
            # Import here to avoid circular imports
            from config.app_settings import get_blog_settings
            blog_data['call_to_action'] = get_blog_settings().call_to_action
            
            return blog_data
            
        except Exception as e:
            logger.error(f"Error parsing blog response: {str(e)}")
            return {
                'title': 'Blog Post Generation Error',
                'summary': 'An error occurred during blog post generation.',
                'content': response_content,
                'category': category,
                'style_persona': category_config.get('style_persona', 'Tech Expert'),
                'key_elements': ['user sovereignty', 'AI ownership'],
                'call_to_action': 'Join the Internet of Value & Freedom'
            }
    
    def embed_media_in_content(self, blog_data: Dict[str, Any], image_data: Dict[str, Any] = None, meme_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Embed generated images and memes into blog post content"""
        try:
            content = blog_data.get('content', '')
            
            # Parse HTML content to find insertion points
            enhanced_content = self._insert_media_in_html(content, image_data, meme_data)
            
            # Update blog data with enhanced content and media metadata
            updated_blog_data = {
                **blog_data,
                'content': enhanced_content,
                'media': {
                    'featured_image': image_data.get('image_url') if image_data and image_data.get('success') else None,
                    'thumbnail_url': image_data.get('thumbnail_url') if image_data and image_data.get('success') else None,
                    'meme_url': meme_data.get('meme_url') if meme_data and meme_data.get('meme_url') else None,
                    'meme_type': meme_data.get('meme_type') if meme_data and meme_data.get('meme_url') else None,
                    'image_alt_text': image_data.get('alt_text') if image_data and image_data.get('success') else None,
                    'meme_alt_text': meme_data.get('alt_text') if meme_data and meme_data.get('meme_url') else None,
                    'image_caption': image_data.get('caption') if image_data and image_data.get('success') else None,
                    'meme_description': meme_data.get('meme_description') if meme_data and meme_data.get('meme_url') else None
                }
            }
            
            logger.info("✅ Media successfully embedded in blog content")
            return updated_blog_data
            
        except Exception as e:
            logger.error(f"❌ Error embedding media in content: {str(e)}")
            # Return original blog data if embedding fails
            return blog_data
    
    def _insert_media_in_html(self, content: str, image_data: Dict[str, Any], meme_data: Dict[str, Any]) -> str:
        """Insert media elements into HTML content at appropriate positions"""
        try:
            # Clean up content and ensure it's properly formatted
            if not content.strip().startswith('<'):
                # If not HTML, wrap in basic structure
                content = f"<div>{content}</div>"
            
            # Insert meme at the beginning (after any existing opening tags)
            if meme_data and meme_data.get('meme_url'):
                meme_html = self._create_meme_html(meme_data)
                content = self._insert_at_beginning(content, meme_html)
            
            # Insert featured image in the middle of content
            if image_data and image_data.get('success'):
                image_html = self._create_image_html(image_data)
                content = self._insert_in_middle(content, image_html)
            
            return content
            
        except Exception as e:
            logger.error(f"Error inserting media in HTML: {str(e)}")
            return content
    
    def _create_meme_html(self, meme_data: Dict[str, Any]) -> str:
        """Create HTML for meme display - clean presentation without technical details"""
        meme_url = meme_data.get('meme_url')
        
        if meme_url and meme_url != 'text_only':
            # Generated meme image - clean presentation
            return (f'<div class="blog-meme" style="text-align: center; margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 8px;">'
                   f'<img src="{meme_url}" alt="{meme_data.get("alt_text", "Meme")}" style="max-width: 100%; height: auto; border-radius: 8px;" />'
                   f'</div>')
        else:
            # Text-only meme fallback - simple and clean
            return (f'<div class="blog-meme-text" style="text-align: center; margin: 20px 0; padding: 20px; background-color: #f0f8ff; border-left: 4px solid #DDBC74; border-radius: 8px;">'
                   f'<div style="font-size: 1.2em; margin-bottom: 8px;">❌ {meme_data.get("top_text", "Old way")}</div>'
                   f'<div style="font-size: 1.2em; font-weight: bold;">✅ {meme_data.get("bottom_text", "BrainCargo way")}</div>'
                   f'</div>')
    
    def _create_image_html(self, image_data: Dict[str, Any]) -> str:
        """Create HTML for featured image display"""
        caption_html = f'<figcaption style="margin-top: 15px; font-style: italic; color: #666; font-size: 0.95em;">{image_data.get("caption", "")}</figcaption>' if image_data.get('caption') else ''
        return (f'<figure class="blog-featured-image" style="margin: 30px 0; text-align: center;">'
               f'<img src="{image_data["image_url"]}" alt="{image_data.get("alt_text", "Blog featured image")}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />'
               f'{caption_html}'
               f'</figure>')
    
    def _insert_at_beginning(self, content: str, insert_html: str) -> str:
        """Insert HTML at the beginning of content (after opening tags)"""
        # Find the first significant content (after potential opening divs/headers)
        import re
        
        # Look for the first paragraph, h1, h2, etc.
        match = re.search(r'(<(?:h[1-6]|p|div[^>]*>(?![^<]*</div>)))', content, re.IGNORECASE)
        if match:
            insert_pos = match.start()
            return content[:insert_pos] + insert_html + content[insert_pos:]
        else:
            # If no clear insertion point, insert after opening tag
            if content.startswith('<div>'):
                return content[:5] + insert_html + content[5:]
            else:
                return insert_html + content
    
    def _insert_in_middle(self, content: str, insert_html: str) -> str:
        """Insert HTML in the middle of content (between paragraphs)"""
        import re
        
        # Find all paragraph or heading tags
        tags = list(re.finditer(r'</(p|h[1-6]|div)>', content, re.IGNORECASE))
        
        if len(tags) > 2:
            # Insert after the middle paragraph
            middle_pos = len(tags) // 2
            insert_pos = tags[middle_pos].end()
            return content[:insert_pos] + insert_html + content[insert_pos:]
        elif len(tags) >= 1:
            # Insert after the first paragraph
            insert_pos = tags[0].end()
            return content[:insert_pos] + insert_html + content[insert_pos:]
        else:
            # If no clear paragraphs, append to end
            return content + insert_html


def extract_content_from_url(url: str) -> Dict[str, Any]:
    """Extract content from a URL for blog generation"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extract main content
        # Try common content selectors
        content_selectors = [
            'article', '.content', '.post-content', '.entry-content',
            'main', '.main-content', '#content', '.article-content'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content_text = content_elem.get_text(separator=' ', strip=True)
                break
        
        # Fallback to body if no specific content found
        if not content_text:
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)
        
        return {
            'success': True,
            'title': title_text,
            'content': content_text,
            'url': url
        }
        
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'title': "",
            'content': "",
            'url': url
        } 