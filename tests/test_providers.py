"""
Unit tests for AI provider system.

Tests the base provider interface, individual providers,
and the provider factory.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from providers.base import BaseLLMProvider
from providers.factory import LLMProviderFactory
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider


class TestBaseLLMProvider(unittest.TestCase):
    """Test the base LLM provider interface."""

    def test_base_provider_is_abstract(self):
        """Test that BaseLLMProvider cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseLLMProvider()

    def test_base_provider_interface(self):
        """Test that the base provider defines the required interface."""
        # Check that required methods exist
        self.assertTrue(hasattr(BaseLLMProvider, 'generate_completion'))
        self.assertTrue(hasattr(BaseLLMProvider, 'is_available'))
        self.assertTrue(hasattr(BaseLLMProvider, '_initialize_client'))


class MockProvider(BaseLLMProvider):
    """Mock provider for testing the base functionality."""
    
    def __init__(self, is_available: bool = True):
        # Create mock config
        config = {
            'type': 'mock_provider',
            'models': {'standard': 'mock-model'},
            'default_temperature': 0.7,
            'max_tokens': 4000
        }
        super().__init__(config)
        self._is_available = is_available

    def _initialize_client(self):
        """Mock client initialization."""
        self.client = "mock_client"

    def generate_completion(self, prompt: str, model: str = "standard", **kwargs) -> Dict[str, Any]:
        """Mock completion generation."""
        return {
            "content": "Mock completion content",
            "model": model,
            "success": True
        }

    def is_available(self) -> bool:
        """Mock availability check."""
        return self._is_available


class TestProviderImplementation(unittest.TestCase):
    """Test provider implementation using mock provider."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = MockProvider()

    def test_provider_generate_completion(self):
        """Test completion generation functionality."""
        result = self.provider.generate_completion("Test prompt")
        
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
        self.assertIn('model', result)
        self.assertIn('success', result)
        
        self.assertEqual(result['content'], "Mock completion content")
        self.assertTrue(result['success'])

    def test_provider_availability(self):
        """Test provider availability check."""
        available_provider = MockProvider(is_available=True)
        unavailable_provider = MockProvider(is_available=False)
        
        self.assertTrue(available_provider.is_available())
        self.assertFalse(unavailable_provider.is_available())

    def test_provider_type(self):
        """Test provider type property."""
        self.assertEqual(self.provider.provider_type, "mock_provider")


class TestOpenAIProvider(unittest.TestCase):
    """Test OpenAI provider implementation."""

    def test_openai_provider_availability_without_key(self):
        """Test availability when no API key is provided."""
        config = {'type': 'openai', 'api_key_env': 'NONEXISTENT_KEY', 'models': {'standard': 'gpt-4o'}}
        provider = OpenAIProvider(config)
        self.assertFalse(provider.is_available())

    def test_openai_provider_type(self):
        """Test OpenAI provider type."""
        config = {'type': 'openai', 'api_key_env': 'OPENAI_API_KEY', 'models': {'standard': 'gpt-4o'}}
        provider = OpenAIProvider(config)
        self.assertEqual(provider.provider_type, "openai")


class TestAnthropicProvider(unittest.TestCase):
    """Test Anthropic provider implementation."""

    def test_anthropic_provider_availability_without_key(self):
        """Test availability when no API key is provided."""
        config = {'type': 'anthropic', 'api_key_env': 'NONEXISTENT_KEY', 'models': {'standard': 'claude-3-5-sonnet-20241022'}}
        provider = AnthropicProvider(config)
        self.assertFalse(provider.is_available())

    def test_anthropic_provider_type(self):
        """Test Anthropic provider type."""
        config = {'type': 'anthropic', 'api_key_env': 'ANTHROPIC_API_KEY', 'models': {'standard': 'claude-3-5-sonnet-20241022'}}
        provider = AnthropicProvider(config)
        self.assertEqual(provider.provider_type, "anthropic")


class TestLLMProviderFactory(unittest.TestCase):
    """Test the LLM provider factory."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = LLMProviderFactory()

    def test_factory_initialization(self):
        """Test factory initialization."""
        self.assertIsInstance(self.factory, LLMProviderFactory)

    def test_create_openai_provider(self):
        """Test creating OpenAI provider through factory."""
        config = {'type': 'openai', 'api_key_env': 'NONEXISTENT_KEY', 'models': {'standard': 'gpt-4o'}}
        provider = self.factory.create_provider("openai", config)
        
        self.assertIsNotNone(provider)
        self.assertEqual(provider.provider_type, "openai")

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider through factory."""
        config = {'type': 'anthropic', 'api_key_env': 'NONEXISTENT_KEY', 'models': {'standard': 'claude-3-5-sonnet-20241022'}}
        provider = self.factory.create_provider("anthropic", config)
        
        self.assertIsNotNone(provider)
        self.assertEqual(provider.provider_type, "anthropic")

    def test_create_invalid_provider(self):
        """Test creating an invalid provider type."""
        config = {'type': 'invalid_provider', 'api_key_env': 'TEST_KEY'}
        provider = self.factory.create_provider("invalid_provider", config)
        self.assertIsNone(provider)

    def test_get_available_providers(self):
        """Test getting available provider classes."""
        providers = self.factory.get_available_providers()
        
        self.assertIsInstance(providers, dict)
        self.assertIn('openai', providers)
        self.assertIn('anthropic', providers)

    def test_create_multiple_providers(self):
        """Test creating multiple providers."""
        configs = {
            'openai_test': {'type': 'openai', 'api_key_env': 'OPENAI_API_KEY'},
            'anthropic_test': {'type': 'anthropic', 'api_key_env': 'ANTHROPIC_API_KEY'},
            'invalid_test': {'type': 'invalid', 'api_key_env': 'INVALID_KEY'}
        }
        
        providers = self.factory.create_multiple_providers(configs)
        
        # Should return dict, might be empty if API keys not available
        self.assertIsInstance(providers, dict)


if __name__ == '__main__':
    unittest.main() 