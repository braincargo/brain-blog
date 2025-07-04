"""
Unit tests for configuration management.

Tests the BlogSettings, SecuritySettings, and APISettings classes
to ensure proper configuration validation and loading.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from dataclasses import FrozenInstanceError

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.app_settings import BlogSettings, SecuritySettings, APISettings, get_settings


class TestBlogSettings(unittest.TestCase):
    """Test BlogSettings configuration class."""

    def test_blog_settings_creation(self):
        """Test creating BlogSettings with valid data."""
        settings = BlogSettings(
            domain="testdomain.com",
            company_name="Test Company",
            cdn_base_url="https://cdn.testdomain.com",
            call_to_action="Visit our site"
        )
        
        self.assertEqual(settings.domain, "testdomain.com")
        self.assertEqual(settings.company_name, "Test Company")
        self.assertEqual(settings.cdn_base_url, "https://cdn.testdomain.com")
        self.assertEqual(settings.call_to_action, "Visit our site")

    def test_blog_settings_defaults(self):
        """Test BlogSettings with default values."""
        settings = BlogSettings()
        
        self.assertEqual(settings.domain, "braincargo.com")
        self.assertEqual(settings.cdn_base_url, "https://braincargo.com")
        self.assertEqual(settings.call_to_action, "Join the Internet of Value & Freedom at braincargo.com")
        self.assertEqual(settings.company_name, "BrainCargo LLC")

    def test_blog_settings_mutable(self):
        """Test that BlogSettings allows modification."""
        settings = BlogSettings(
            domain="testdomain.com",
            company_name="Test Company"
        )
        
        # Should be able to modify fields
        settings.domain = "newdomain.com"
        self.assertEqual(settings.domain, "newdomain.com")

    def test_blog_settings_validation_url(self):
        """Test URL validation in BlogSettings."""
        # Valid URLs should not raise exceptions
        BlogSettings(
            domain="testdomain.com",
            company_name="Test Company",
            cdn_base_url="https://cdn.testdomain.com"
        )
        
        BlogSettings(
            domain="testdomain.com", 
            company_name="Test Company",
            cdn_base_url="https://cdn.testdomain.com"
        )


class TestSecuritySettings(unittest.TestCase):
    """Test SecuritySettings configuration class."""

    def test_security_settings_creation(self):
        """Test creating SecuritySettings with valid data."""
        settings = SecuritySettings(
            authorized_phone_number="1234567890"
        )
        
        self.assertEqual(settings.authorized_phone_number, "1234567890")

    def test_security_settings_defaults(self):
        """Test SecuritySettings with default values."""
        settings = SecuritySettings()
        
        self.assertEqual(settings.authorized_phone_number, "")

    def test_security_settings_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers (digits only)
        SecuritySettings(authorized_phone_number="1234567890")
        SecuritySettings(authorized_phone_number="12345678901")
        SecuritySettings(authorized_phone_number="")  # Empty is valid (disabled)


class TestAPISettings(unittest.TestCase):
    """Test APISettings configuration class."""

    def test_api_settings_creation(self):
        """Test creating APISettings with valid data."""
        settings = APISettings(
            openai_api_key="test-openai-key",
            anthropic_api_key="test-anthropic-key"
        )
        
        self.assertEqual(settings.openai_api_key, "test-openai-key")
        self.assertEqual(settings.anthropic_api_key, "test-anthropic-key")

    def test_api_settings_defaults(self):
        """Test APISettings with default values."""
        settings = APISettings()
        
        self.assertEqual(settings.openai_api_key, "")
        self.assertEqual(settings.anthropic_api_key, "")
        self.assertEqual(settings.aws_access_key, "")
        self.assertEqual(settings.aws_secret_key, "")
        self.assertEqual(settings.blog_posts_bucket, "")


class TestConfigurationLoading(unittest.TestCase):
    """Test configuration loading from environment variables."""

    @patch.dict(os.environ, {
        'BLOG_DOMAIN': 'testdomain.com',
        'COMPANY_NAME': 'Test Company',
        'CDN_BASE_URL': 'https://cdn.testdomain.com',
        'BLOG_CALL_TO_ACTION': 'Visit our site',
        'AUTHORIZED_PHONE_NUMBER': '1234567890',
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'DEBUG': 'true'
    })
    def test_load_configuration_from_env(self):
        """Test loading configuration from environment variables."""
        from config.app_settings import reload_settings
        config = reload_settings()
        
        # Check blog settings
        self.assertEqual(config.blog.domain, 'testdomain.com')
        self.assertEqual(config.blog.company_name, 'Test Company')
        self.assertEqual(config.blog.cdn_base_url, 'https://cdn.testdomain.com')
        self.assertEqual(config.blog.call_to_action, 'Visit our site')
        
        # Check security settings
        self.assertEqual(config.security.authorized_phone_number, '1234567890')
        
        # Check API settings
        self.assertEqual(config.api.openai_api_key, 'test-openai-key')
        self.assertEqual(config.api.anthropic_api_key, 'test-anthropic-key')

    @patch.dict(os.environ, {}, clear=True)
    def test_load_configuration_defaults(self):
        """Test loading configuration with default values when env vars are missing."""
        from config.app_settings import reload_settings
        config = reload_settings()
        
        # Check that defaults are applied
        self.assertEqual(config.blog.domain, 'braincargo.com')
        self.assertEqual(config.blog.company_name, 'BrainCargo LLC')
        self.assertEqual(config.blog.call_to_action, 'Join the Internet of Value & Freedom at braincargo.com')
        
        self.assertEqual(config.security.authorized_phone_number, '')
        
        self.assertEqual(config.api.openai_api_key, '')

    @patch.dict(os.environ, {
        'BLOG_DOMAIN': 'testdomain.com',
        'COMPANY_NAME': 'Test Company',
        'AUTHORIZED_PHONE_NUMBER': ''  # Empty phone disables auth
    })
    def test_phone_auth_disabled_when_empty(self):
        """Test that phone auth is disabled when phone number is empty."""
        from config.app_settings import reload_settings
        config = reload_settings()
        
        self.assertEqual(config.security.authorized_phone_number, '')

    @patch.dict(os.environ, {
        'BLOG_DOMAIN': 'testdomain.com',
        'COMPANY_NAME': 'Test Company',
        'AUTHORIZED_PHONE_NUMBER': '1234567890'  # Non-empty phone enables auth
    })
    def test_phone_auth_enabled_when_set(self):
        """Test that phone auth is enabled when phone number is provided."""
        from config.app_settings import reload_settings
        config = reload_settings()
        
        self.assertEqual(config.security.authorized_phone_number, '1234567890')

    def test_configuration_validation(self):
        """Test configuration validation for missing required settings."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_settings()
            
            # Test that we can get the configuration even with empty environment
            self.assertIsNotNone(config)
            self.assertIsNotNone(config.blog)
            self.assertIsNotNone(config.security)
            self.assertIsNotNone(config.api)


if __name__ == '__main__':
    unittest.main() 