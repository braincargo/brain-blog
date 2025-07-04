"""
Test package for Brain Blog Generator.

This package contains all unit tests, integration tests, and test utilities
for the Brain Blog Generator application.
"""

import os
import sys
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import the main modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test configuration constants
TEST_CONFIG = {
    'OPENAI_API_KEY': 'test-openai-key',
    'ANTHROPIC_API_KEY': 'test-anthropic-key',
    'BLOG_DOMAIN': 'testdomain.com',
    'COMPANY_NAME': 'Test Company',
    'DEBUG': True
}

# Mock responses for consistent testing
MOCK_BLOG_RESPONSE = {
    'title': 'Test Blog Post',
    'content': '<h1>Test Blog Post</h1><p>This is a test blog post content.</p>',
    'summary': 'A test blog post for unit testing purposes.',
    'category': 'Technology'
}

MOCK_URL_CONTENT = {
    'title': 'Test Article',
    'content': 'This is test content from a mocked URL.',
    'meta_description': 'Test article description'
}

def create_mock_provider():
    """Create a mock AI provider for testing."""
    mock_provider = MagicMock()
    mock_provider.generate_blog.return_value = MOCK_BLOG_RESPONSE
    mock_provider.is_available.return_value = True
    mock_provider.provider_name = 'mock_provider'
    return mock_provider 