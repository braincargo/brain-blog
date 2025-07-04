#!/usr/bin/env python3
"""
Single Blog Generator - Generate one specific blog post by index
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blog_links_processor import BlogLinksProcessor
from pipeline.pipeline_manager import PipelineManager
from app import fetch_url_content

def generate_single_blog(index=8):
    """Generate a single blog post by index"""
    
    print(f"🚀 Single Blog Generator - Index {index}")
    print("=" * 50)
    
    # Load links
    print("📚 Loading links...")
    processor = BlogLinksProcessor("../blog_links.txt")
    try:
        links = processor.load_links()
    except FileNotFoundError:
        print("❌ blog_links.txt not found")
        return False
    
    if index >= len(links):
        print(f"❌ Index {index} is out of range. File has {len(links)} links.")
        return False
    
    url = links[index]
    print(f"🔗 URL to process: {url}")
    
    # Initialize pipeline
    print("🔧 Initializing pipeline...")
    try:
        config_path = "config/pipeline.yaml"
        pipeline_manager = PipelineManager(config_path)
        print("✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {str(e)}")
        return False
    
    # Generate output directory in parent
    output_dir = Path("../generated_blogs")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Fetch content
        print(f"🌐 Fetching content...")
        content_data = fetch_url_content(url)
        
        if not content_data or not content_data.get('content'):
            print(f"❌ Failed to fetch content from URL")
            return False
        
        content_length = len(content_data['content'])
        print(f"📄 Extracted {content_length} characters")
        
        # Process through pipeline
        print(f"🚀 Running through AI pipeline with o3-pro...")
        start_time = time.time()
        
        result = pipeline_manager.process_url(
            url=url,
            content=content_data['content'],
            custom_title=""
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if not result.get('success'):
            print(f"❌ Pipeline failed: {result.get('error')}")
            return False
        
        # Extract blog data
        blog_step = result.get('pipeline_steps', {}).get('blog_generation', {})
        if not blog_step.get('success'):
            print(f"❌ Blog generation step failed")
            return False
        
        blog_data = blog_step.get('data', {})
        
        # Show results
        steps_completed = list(result.get('pipeline_steps', {}).keys())
        print(f"\n🎯 Pipeline steps completed: {', '.join(steps_completed)}")
        print(f"⏱️ Processing took {duration:.1f} seconds")
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in blog_data.get('title', 'untitled')[:50] 
                           if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        blog_index = index + 1  # Convert to 1-based indexing for filename
        base_filename = f"blog_{blog_index:03d}_{timestamp}_{safe_title}"
        
        # Save JSON
        json_file = output_dir / f"{base_filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'index': blog_index,
                'source_url': url,
                'blog_data': blog_data,
                'pipeline_steps': steps_completed,
                'pipeline_success': result.get('success'),
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0.0'
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS!")
        print(f"📝 Generated: {blog_data.get('title', 'Untitled')}")
        print(f"📁 Category: {blog_data.get('category', 'N/A')}")
        print(f"📄 Content: {len(blog_data.get('content', ''))} characters")
        print(f"💾 Saved: {json_file.name}")
        
        # Show media
        media = blog_data.get('media', {})
        if media.get('featured_image'):
            print(f"🖼️ Featured image: {media['featured_image']}")
        if media.get('meme_url'):
            print(f"😄 Meme: {media['meme_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Generate a single blog post by index')
    parser.add_argument('--index', type=int, default=8, help='URL index to process (default: 8)')
    args = parser.parse_args()
    
    success = generate_single_blog(args.index)
    
    if success:
        print(f"\n🎉 Blog generation complete!")
        print(f"📁 Check ../generated_blogs/ for the result")
    else:
        print(f"\n❌ Blog generation failed!")

if __name__ == "__main__":
    main() 