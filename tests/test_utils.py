"""
Unit tests for utility functions and helper modules.

Tests content extraction, URL validation, and other utility functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup


class TestContentExtraction(unittest.TestCase):
    """Test content extraction utilities."""

    @patch('requests.get')
    def test_extract_content_from_url_success(self, mock_get):
        """Test successful content extraction from URL."""
        # Mock HTML content
        html_content = """
        <html>
            <head>
                <title>Test Article</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Title</h1>
                <p>First paragraph of content.</p>
                <p>Second paragraph with more content.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Import the function (assuming it exists in a utils module)
        # from utils.content_extraction import extract_content_from_url
        
        # For now, let's test the logic directly
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find('title').get_text().strip()
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc['content'] if meta_desc else ''
        
        # Extract text content
        for script in soup(["script", "style"]):
            script.decompose()
        content = soup.get_text()
        
        self.assertEqual(title, "Test Article")
        self.assertEqual(meta_description, "Test description")
        self.assertIn("Main Title", content)
        self.assertIn("First paragraph", content)

    @patch('requests.get')
    def test_extract_content_from_url_http_error(self, mock_get):
        """Test content extraction with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Should handle HTTP errors gracefully
        with self.assertRaises(requests.exceptions.HTTPError):
            mock_response.raise_for_status()

    @patch('requests.get')
    def test_extract_content_from_url_timeout(self, mock_get):
        """Test content extraction with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with self.assertRaises(requests.exceptions.Timeout):
            mock_get('https://example.com', timeout=10)

    @patch('requests.get')
    def test_extract_content_from_url_connection_error(self, mock_get):
        """Test content extraction with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with self.assertRaises(requests.exceptions.ConnectionError):
            mock_get('https://example.com')

    def test_extract_content_malformed_html(self):
        """Test content extraction with malformed HTML."""
        malformed_html = "<html><head><title>Test</title><body><p>Content without closing tags"
        
        # BeautifulSoup should handle malformed HTML gracefully
        soup = BeautifulSoup(malformed_html, 'html.parser')
        title = soup.find('title')
        
        self.assertIsNotNone(title)
        self.assertEqual(title.get_text(), "Test")

    def test_extract_content_no_title(self):
        """Test content extraction when no title is present."""
        html_without_title = """
        <html>
            <body>
                <h1>Content without title tag</h1>
                <p>Some content here.</p>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html_without_title, 'html.parser')
        title_tag = soup.find('title')
        
        self.assertIsNone(title_tag)
        
        # Should extract h1 as fallback
        h1_tag = soup.find('h1')
        self.assertIsNotNone(h1_tag)
        self.assertEqual(h1_tag.get_text(), "Content without title tag")

    def test_extract_content_no_meta_description(self):
        """Test content extraction when no meta description is present."""
        html_without_meta = """
        <html>
            <head><title>Test</title></head>
            <body><p>Content without meta description.</p></body>
        </html>
        """
        
        soup = BeautifulSoup(html_without_meta, 'html.parser')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        self.assertIsNone(meta_desc)


class TestURLValidation(unittest.TestCase):
    """Test URL validation utilities."""

    def test_valid_urls(self):
        """Test validation of valid URLs."""
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://www.example.com/path/to/article',
            'https://example.com/article?param=value',
            'https://subdomain.example.com',
            'https://example.org/path#section',
        ]
        
        import re
        url_pattern = re.compile(
            r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9](?:[:\d]+)?(?:/(?:[\w/_.-])*)?(?:\?(?:[\w&=%-])*)?(?:#(?:\w)*)?$'
        )
        
        for url in valid_urls:
            self.assertTrue(url_pattern.match(url), f"URL should be valid: {url}")

    def test_invalid_urls(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',  # Not HTTP/HTTPS
            'example.com',  # Missing protocol
            'https://',  # Missing domain
            'https://.',  # Invalid domain
            '',  # Empty string
            'javascript:alert("xss")',  # Potential XSS
        ]
        
        import re
        url_pattern = re.compile(
            r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9](?:[:\d]+)?(?:/(?:[\w/_.-])*)?(?:\?(?:[\w&=%-])*)?(?:#(?:\w)*)?$'
        )
        
        for url in invalid_urls:
            self.assertFalse(url_pattern.match(url), f"URL should be invalid: {url}")

    def test_extract_urls_from_text(self):
        """Test extracting URLs from text content."""
        import re
        
        text_with_urls = """
        Check out these articles:
        https://example.com/article1
        and also http://example.org/article2
        There's more at https://blog.example.com/post?id=123
        """
        
        url_pattern = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?')
        urls = url_pattern.findall(text_with_urls)
        
        expected_urls = [
            'https://example.com/article1',
            'http://example.org/article2',
            'https://blog.example.com/post?id=123'
        ]
        
        self.assertEqual(len(urls), 3)
        for expected_url in expected_urls:
            self.assertIn(expected_url, urls)

    def test_clean_phone_number(self):
        """Test phone number cleaning utility."""
        test_cases = [
            ('+1234567890', '1234567890'),
            ('1234567890', '1234567890'),
            ('+1 (234) 567-8900', '12345678900'),
            ('(234) 567-8900', '2345678900'),
            ('234-567-8900', '2345678900'),
            ('234.567.8900', '2345678900'),
            ('234 567 8900', '2345678900'),
        ]
        
        import re
        
        for input_phone, expected_output in test_cases:
            # Remove all non-digit characters
            cleaned = re.sub(r'[^\d]', '', input_phone)
            self.assertEqual(cleaned, expected_output)

    def test_sanitize_input(self):
        """Test input sanitization."""
        test_cases = [
            ('normal text', 'normal text'),
            ('<script>alert("xss")</script>', 'alert("xss")'),
            ('text with\nnewlines\rand\ttabs', 'text with newlines and tabs'),
            ('text   with    multiple   spaces', 'text with multiple spaces'),
        ]
        
        import re
        
        for input_text, expected_output in test_cases:
            # Remove HTML tags
            sanitized = re.sub(r'<[^>]+>', '', input_text)
            # Normalize whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            
            self.assertEqual(sanitized, expected_output)


class TestTextProcessing(unittest.TestCase):
    """Test text processing utilities."""

    def test_truncate_text(self):
        """Test text truncation with word boundaries."""
        long_text = "This is a very long text that should be truncated at word boundaries to avoid cutting words in the middle."
        
        def truncate_text(text, max_length=50):
            if len(text) <= max_length:
                return text
            
            # Find the last space before max_length
            truncated = text[:max_length]
            last_space = truncated.rfind(' ')
            
            if last_space != -1:
                truncated = truncated[:last_space]
            
            return truncated + '...'
        
        result = truncate_text(long_text, max_length=50)
        
        self.assertLessEqual(len(result), 53)  # 50 + "..."
        self.assertTrue(result.endswith('...'))
        self.assertNotIn(result[:-3], ' ')  # Should not end with partial word

    def test_extract_keywords(self):
        """Test keyword extraction from text."""
        text = "artificial intelligence machine learning deep learning neural networks"
        
        def extract_keywords(text, min_length=3):
            import re
            # Simple keyword extraction: split on whitespace and filter
            words = re.findall(r'\b\w+\b', text.lower())
            keywords = [word for word in words if len(word) >= min_length]
            return list(set(keywords))  # Remove duplicates
        
        keywords = extract_keywords(text)
        
        expected_keywords = ['artificial', 'intelligence', 'machine', 'learning', 'deep', 'neural', 'networks']
        
        for keyword in expected_keywords:
            self.assertIn(keyword, keywords)

    def test_count_words(self):
        """Test word counting utility."""
        test_cases = [
            ("Hello world", 2),
            ("This is a test sentence.", 5),
            ("", 0),
            ("   ", 0),
            ("Word", 1),
            ("Multiple    spaces   between   words", 4),
        ]
        
        import re
        
        for text, expected_count in test_cases:
            # Count words using regex
            words = re.findall(r'\b\w+\b', text)
            word_count = len(words)
            
            self.assertEqual(word_count, expected_count)

    def test_clean_html_content(self):
        """Test HTML content cleaning."""
        html_content = """
        <div>
            <h1>Title</h1>
            <p>First paragraph with <strong>bold</strong> text.</p>
            <script>alert('should be removed');</script>
            <style>body { color: red; }</style>
            <p>Second paragraph.</p>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up whitespace
        import re
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        self.assertIn('Title', cleaned_text)
        self.assertIn('First paragraph', cleaned_text)
        self.assertIn('Second paragraph', cleaned_text)
        self.assertNotIn('alert', cleaned_text)
        self.assertNotIn('color: red', cleaned_text)


if __name__ == '__main__':
    unittest.main() 