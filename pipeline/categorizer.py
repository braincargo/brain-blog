"""
URL Categorizer - Classifies content into categories using AI
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class URLCategorizer:
    """Categorizes URLs and content into defined categories using LLM providers"""
    
    # Default categories for blog content
    DEFAULT_CATEGORIES = [
        'technology', 'ai-ml', 'blockchain', 'web3', 'cybersecurity', 
        'software-development', 'data-science', 'business', 'finance',
        'startup', 'innovation', 'news', 'opinion', 'tutorial', 'review'
    ]
    
    def __init__(self, config: Dict[str, Any], providers: Dict[str, Any]):
        self.config = config
        self.providers = providers
        self.categories = config.get('categories', self.DEFAULT_CATEGORIES)
        self.fallback_category = config.get('fallback_category', 'technology')
        
    def categorize(self, url: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        Categorize URL content using LLM provider
        
        Args:
            url: Source URL
            content: Content text to categorize
            title: Optional title for additional context
            
        Returns:
            Dict with category, confidence, and reasoning
        """
        try:
            # Try to use LLM provider for intelligent categorization
            if self.providers:
                return self._categorize_with_llm(url, content, title)
            else:
                # Fallback to rule-based categorization
                return self._categorize_with_rules(url, content, title)
                
        except Exception as e:
            logger.error(f"❌ Categorization failed: {str(e)}")
            return {
                'success': False,
                'category': self.fallback_category,
                'confidence': 0.3,
                'reasoning': f'Error during categorization: {str(e)}',
                'secondary_category': None,
                'method': 'error_fallback'
            }
    
    def _categorize_with_llm(self, url: str, content: str, title: str) -> Dict[str, Any]:
        """Use LLM provider for intelligent categorization"""
        
        # Get the first available provider
        provider = next(iter(self.providers.values())) if self.providers else None
        if not provider or not provider.is_available():
            return self._categorize_with_rules(url, content, title)
        
        # Prepare categorization prompt
        categories_list = ", ".join(self.categories)
        
        prompt = f"""Analyze the following content and categorize it into one of these categories: {categories_list}

URL: {url}
Title: {title}
Content: {content[:1000]}...

Instructions:
1. Choose the MOST appropriate category from the list above
2. Provide a confidence score (0.0 to 1.0)
3. Give a brief reasoning for your choice
4. Optionally suggest a secondary category if relevant

Respond in this exact JSON format:
{{
    "category": "selected_category",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this category fits",
    "secondary_category": "optional_secondary_category_or_null"
}}"""

        try:
            # Generate categorization using LLM
            result = provider.generate_completion(
                prompt=prompt,
                model="fast",  # Use fast model for categorization
                temperature=0.3,  # Low temperature for consistent results
                max_tokens=200,
                output_format="json"
            )
            
            if result.get('success') and result.get('content'):
                # Parse JSON response
                import json
                try:
                    categorization = json.loads(result['content'].strip())
                    
                    # Validate category is in our list
                    category = categorization.get('category', self.fallback_category)
                    if category not in self.categories:
                        category = self.fallback_category
                        confidence = 0.5
                        reasoning = f"LLM suggested unknown category, using fallback: {category}"
                    else:
                        confidence = min(max(categorization.get('confidence', 0.7), 0.0), 1.0)
                        reasoning = categorization.get('reasoning', 'AI categorization')
                    
                    return {
                        'success': True,
                        'category': category,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'secondary_category': categorization.get('secondary_category'),
                        'method': 'llm',
                        'provider': result.get('provider', 'unknown')
                    }
                    
                except json.JSONDecodeError:
                    logger.warning("⚠️ LLM returned invalid JSON, falling back to rules")
                    return self._categorize_with_rules(url, content, title)
            
        except Exception as e:
            logger.error(f"❌ LLM categorization failed: {str(e)}")
        
        # Fallback to rule-based categorization
        return self._categorize_with_rules(url, content, title)
    
    def _categorize_with_rules(self, url: str, content: str, title: str) -> Dict[str, Any]:
        """Fallback rule-based categorization using keywords and patterns"""
        
        # Combine text for analysis
        text = f"{title} {content}".lower()
        url_lower = url.lower()
        
        # Rule-based categorization
        category_scores = {}
        
        # Technology keywords
        tech_keywords = ['api', 'software', 'programming', 'code', 'developer', 'tech', 'computer']
        category_scores['technology'] = sum(1 for keyword in tech_keywords if keyword in text)
        
        # AI/ML keywords  
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'deep learning']
        category_scores['ai-ml'] = sum(1 for keyword in ai_keywords if keyword in text)
        
        # Blockchain/Web3 keywords
        crypto_keywords = ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'web3', 'defi', 'nft']
        category_scores['blockchain'] = sum(1 for keyword in crypto_keywords if keyword in text)
        
        # Security keywords
        security_keywords = ['security', 'cybersecurity', 'hack', 'vulnerability', 'encryption', 'privacy']
        category_scores['cybersecurity'] = sum(1 for keyword in security_keywords if keyword in text)
        
        # Business keywords
        business_keywords = ['business', 'startup', 'company', 'market', 'strategy', 'growth']
        category_scores['business'] = sum(1 for keyword in business_keywords if keyword in text)
        
        # URL-based hints
        if 'github.com' in url_lower or 'stackoverflow.com' in url_lower:
            category_scores['software-development'] = category_scores.get('software-development', 0) + 2
        elif 'techcrunch.com' in url_lower or 'venturebeat.com' in url_lower:
            category_scores['startup'] = category_scores.get('startup', 0) + 2
        elif 'news' in url_lower:
            category_scores['news'] = category_scores.get('news', 0) + 2
        
        # Find best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[best_category] / 5.0, 0.9)  # Scale confidence
            
            if confidence > 0.3:
                return {
                    'success': True,
                    'category': best_category,
                    'confidence': confidence,
                    'reasoning': f'Rule-based categorization based on keywords and URL patterns',
                    'secondary_category': None,
                    'method': 'rules'
                }
        
        # Default fallback
        return {
            'success': True,
            'category': self.fallback_category,
            'confidence': 0.5,
            'reasoning': 'No strong category indicators found, using default category',
            'secondary_category': None,
            'method': 'fallback'
        }
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories"""
        return self.categories.copy()
    
    def add_custom_category(self, category: str) -> None:
        """Add a custom category to the available list"""
        if category not in self.categories:
            self.categories.append(category)
            logger.info(f"📝 Added custom category: {category}")


# Alias for backward compatibility with tests
ContentCategorizer = URLCategorizer 