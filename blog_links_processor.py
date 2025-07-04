"""
Blog Links Processor - Processes and manages blog link collections
"""

import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BlogLinksProcessor:
    """Processes blog links from files and manages link collections"""
    
    def __init__(self, links_file: str):
        self.links_file = Path(links_file)
        self.links: List[str] = []
    
    def load_links(self) -> List[str]:
        """Load links from the specified file"""
        try:
            if not self.links_file.exists():
                raise FileNotFoundError(f"Links file not found: {self.links_file}")
            
            with open(self.links_file, 'r', encoding='utf-8') as f:
                links = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        links.append(line)
            
            self.links = links
            logger.info(f"Loaded {len(links)} links from {self.links_file}")
            return links
            
        except Exception as e:
            logger.error(f"Error loading links from {self.links_file}: {e}")
            raise
    
    def get_link(self, index: int) -> Optional[str]:
        """Get a specific link by index"""
        if 0 <= index < len(self.links):
            return self.links[index]
        return None
    
    def add_link(self, url: str) -> bool:
        """Add a new link to the collection"""
        try:
            if url not in self.links:
                self.links.append(url)
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding link: {e}")
            return False
    
    def save_links(self) -> bool:
        """Save current links back to file"""
        try:
            with open(self.links_file, 'w', encoding='utf-8') as f:
                for link in self.links:
                    f.write(f"{link}\n")
            
            logger.info(f"Saved {len(self.links)} links to {self.links_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving links to {self.links_file}: {e}")
            return False
    
    def get_links_count(self) -> int:
        """Get total number of links"""
        return len(self.links) 