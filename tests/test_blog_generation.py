#!/usr/bin/env python3
"""
Local Blog Generation Test
Generates a complete blog post with images and memes for local testing
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_test_blog():
    """Generate a test blog post with images and memes"""
    
    try:
        from pipeline.pipeline_manager import PipelineManager
        
        # Initialize pipeline
        logger.info("🔧 Initializing pipeline...")
        pipeline = PipelineManager()
        
        # Check pipeline health
        health = pipeline.health_check()
        logger.info(f"📊 Pipeline health: {health['overall_health']}")
        
        if health['overall_health'] != 'healthy':
            logger.warning("⚠️ Pipeline not fully healthy, but continuing...")
        
        # Test content - AI/Technology article
        test_url = "https://example.com/ai-revolution-2024"
        test_content = """
        The Artificial Intelligence Revolution: Transforming Industries in 2024
        
        Artificial intelligence is rapidly transforming every industry, from healthcare to finance.
        Machine learning algorithms are becoming more sophisticated, enabling breakthrough applications
        in natural language processing, computer vision, and predictive analytics.
        
        Companies are investing billions in AI research and development, leading to innovations
        that seemed impossible just a few years ago. Autonomous vehicles, AI-powered medical
        diagnosis, and intelligent automation are becoming mainstream technologies.
        
        The future promises even more exciting developments as AI continues to evolve and
        integrate into our daily lives. This technological revolution is just beginning.
        """
        
        logger.info(f"🚀 Processing test URL: {test_url}")
        logger.info(f"📄 Content length: {len(test_content)} characters")
        
        # Process through complete pipeline
        result = pipeline.process_url(test_url, test_content, "AI Revolution 2024")
        
        if result['success']:
            logger.info("✅ Blog generation succeeded!")
            
            # Extract the final blog data
            steps = result.get('pipeline_steps', {})
            
            # Show step results
            logger.info("📋 Pipeline step results:")
            for step_name, step_result in steps.items():
                if isinstance(step_result, dict):
                    success = step_result.get('success', False)
                    status = "✅" if success else "❌"
                    logger.info(f"   {status} {step_name}")
                    
                    if not success and step_result.get('error'):
                        logger.info(f"      Error: {step_result['error']}")
            
            # Get final blog data - it should be in the blog_generation step's data
            final_blog_data = None
            
            if 'blog_generation' in steps and steps['blog_generation'].get('success'):
                final_blog_data = steps['blog_generation'].get('data')
                logger.info(f"📦 Found blog data with keys: {list(final_blog_data.keys()) if final_blog_data else 'None'}")
            
            # Debug: Let's see what's actually in the steps
            if not final_blog_data:
                logger.info("🔍 Debugging pipeline steps structure:")
                for step_name, step_data in steps.items():
                    if isinstance(step_data, dict):
                        logger.info(f"   {step_name}: keys = {list(step_data.keys())}")
                        if 'data' in step_data:
                            data = step_data['data']
                            if isinstance(data, dict):
                                logger.info(f"      data keys: {list(data.keys())}")
            
            if final_blog_data:
                # Save the blog post locally
                save_blog_locally(final_blog_data)
                
                # Show summary
                show_blog_summary(final_blog_data)
                
                return final_blog_data
            else:
                logger.error("❌ Could not extract final blog data")
                return None
        else:
            logger.error(f"❌ Blog generation failed: {result.get('error')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Blog generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def save_blog_locally(blog_data):
    """Save the generated blog post to a local file"""
    try:
        # Create output directory
        output_dir = Path("local_output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blog_id = blog_data.get('id', 'unknown')
        filename = f"blog_{blog_id}_{timestamp}.json"
        
        filepath = output_dir / filename
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blog_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Blog saved to: {filepath}")
        
        # Also save HTML version
        html_filename = f"blog_{blog_id}_{timestamp}.html"
        html_filepath = output_dir / html_filename
        
        html_content = create_html_preview(blog_data)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"🌐 HTML preview saved to: {html_filepath}")
        
        return str(filepath)
        
    except Exception as e:
        logger.error(f"❌ Failed to save blog locally: {str(e)}")
        return None

def create_html_preview(blog_data):
    """Create an HTML preview of the blog post"""
    
    title = blog_data.get('title', 'Untitled Blog Post')
    content = blog_data.get('content', '<p>No content available</p>')
    category = blog_data.get('category', 'Unknown')
    created_at = blog_data.get('created_at', datetime.now().isoformat())
    
    # Extract media info
    media = blog_data.get('media', {})
    featured_image = media.get('featured_image')
    meme_url = media.get('meme_url')
    thumbnail_url = media.get('thumbnail_url')
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - BrainCargo Blog</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
        }}
        .title {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.2em;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
        }}
        .category {{
            background: #007acc;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            text-transform: uppercase;
            margin: 0 5px;
        }}
        .media-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #007acc;
        }}
        .media-info h3 {{
            margin-top: 0;
            color: #333;
        }}
        .media-url {{
            font-family: monospace;
            background: #e9ecef;
            padding: 5px 8px;
            border-radius: 3px;
            word-break: break-all;
            font-size: 0.85em;
        }}
        .content {{
            margin: 30px 0;
        }}
        .content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{title}</h1>
            <div class="meta">
                <span class="category">{category}</span>
                <br>
                Generated: {created_at}
            </div>
        </div>
"""
    
    # Add media info section if we have media
    if media:
        html += """
        <div class="media-info">
            <h3>🎨 Generated Media</h3>
"""
        
        if featured_image:
            html += f"""
            <p><strong>Featured Image:</strong><br>
            <span class="media-url">{featured_image}</span></p>
"""
        
        if meme_url:
            html += f"""
            <p><strong>Meme:</strong><br>
            <span class="media-url">{meme_url}</span></p>
"""
        
        if thumbnail_url:
            html += f"""
            <p><strong>Thumbnail:</strong><br>
            <span class="media-url">{thumbnail_url}</span></p>
"""
        
        html += """
        </div>
"""
    
    html += f"""
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>Generated by BrainCargo Blog Service</p>
            <p>Local Test - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def show_blog_summary(blog_data):
    """Show a summary of the generated blog post"""
    
    logger.info("📖 Blog Post Summary:")
    logger.info("=" * 50)
    
    # Basic info
    logger.info(f"Title: {blog_data.get('title', 'Unknown')}")
    logger.info(f"Category: {blog_data.get('category', 'Unknown')}")
    logger.info(f"Style: {blog_data.get('style_persona', 'Unknown')}")
    logger.info(f"Content length: {len(blog_data.get('content', ''))}")
    
    # Media info
    media = blog_data.get('media', {})
    if media:
        logger.info("\n🎨 Media Generated:")
        
        if media.get('featured_image'):
            logger.info(f"   🖼️ Featured Image: {media['featured_image'][:60]}...")
        
        if media.get('meme_url'):
            logger.info(f"   😄 Meme: {media['meme_url'][:60]}...")
        
        if media.get('thumbnail_url'):
            logger.info(f"   🔗 Thumbnail: {media['thumbnail_url'][:60]}...")
        
        # Storage info
        if media.get('storage'):
            storage = media['storage']
            logger.info(f"\n💾 Storage Info:")
            logger.info(f"   Provider: {storage.get('provider', 'Unknown')}")
            logger.info(f"   Saved at: {storage.get('saved_at', 'Unknown')}")
    else:
        logger.info("\n⚠️ No media generated")
    
    # Content preview
    content = blog_data.get('content', '')
    if content:
        # Remove HTML tags for preview
        import re
        text_content = re.sub(r'<[^>]+>', '', content)
        preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
        logger.info(f"\n📄 Content Preview:")
        logger.info(f"   {preview}")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    try:
        logger.info("🧪 Starting Local Blog Generation Test")
        logger.info("=" * 60)
        
        # Check environment
        if not os.environ.get('OPENAI_API_KEY'):
            logger.warning("⚠️ OPENAI_API_KEY not set - image generation may fail")
        
        # Generate blog
        blog_data = generate_test_blog()
        
        if blog_data:
            logger.info("🎉 Blog generation test completed successfully!")
        else:
            logger.error("❌ Blog generation test failed!")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted by user")
        exit(130)
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        exit(1) 