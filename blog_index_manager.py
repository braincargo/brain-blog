"""
Blog Index Manager - Manages blog post indexing and organization
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BlogIndexManager:
    """Manages blog post indexes and metadata"""
    
    def __init__(self, index_file: str = "blog_index.json"):
        self.index_file = index_file
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load blog index from file"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info(f"Creating new blog index: {self.index_file}")
            return {"posts": [], "metadata": {"created": datetime.now().isoformat()}}
        except Exception as e:
            logger.error(f"Error loading blog index: {e}")
            return {"posts": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def add_post(self, post_data: Dict[str, Any]) -> bool:
        """Add a blog post to the index"""
        try:
            post_entry = {
                "id": post_data.get("id"),
                "title": post_data.get("title"),
                "summary": post_data.get("summary"),
                "category": post_data.get("category"),
                "created_at": post_data.get("created_at", datetime.now().isoformat()),
                "url": post_data.get("url"),
                "featured_image": post_data.get("media", {}).get("featured_image")
            }
            
            self.index["posts"].append(post_entry)
            self._save_index()
            logger.info(f"Added post to index: {post_entry['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding post to index: {e}")
            return False
    
    def _save_index(self) -> bool:
        """Save blog index to file"""
        try:
            self.index["metadata"]["updated"] = datetime.now().isoformat()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving blog index: {e}")
            return False


# Global instance
_blog_index_manager: Optional[BlogIndexManager] = None


def get_blog_index_manager() -> BlogIndexManager:
    """Get global blog index manager instance"""
    global _blog_index_manager
    if _blog_index_manager is None:
        _blog_index_manager = BlogIndexManager()
    return _blog_index_manager


def add_blog_post_to_index(post_data: Dict[str, Any]) -> bool:
    """Add a blog post to the global index"""
    manager = get_blog_index_manager()
    return manager.add_post(post_data)


def sync_blog_indexes() -> bool:
    """Sync blog indexes (placeholder for future implementation)"""
    logger.info("Blog index sync requested")
    return True


def rebuild_blog_index() -> bool:
    """Rebuild blog index (placeholder for future implementation)"""
    logger.info("Blog index rebuild requested")
    return True 