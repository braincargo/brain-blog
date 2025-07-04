"""
LLM Provider Factory
"""

import logging
from typing import Dict, Any, Optional, Type, Union

from .base import BaseLLMProvider, BaseImageProvider, MultiModalProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .grok_provider import GrokProvider
from .gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory class for creating LLM providers"""
    
    # Registry of available providers
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'grok': GrokProvider,
        'gemini': GeminiProvider,
    }
    
    @classmethod
    def create_provider(
        cls, 
        provider_type: str, 
        config: Dict[str, Any]
    ) -> Optional[BaseLLMProvider]:
        """
        Create a provider instance
        
        Args:
            provider_type: Type of provider (openai, anthropic, etc.)
            config: Provider configuration
            
        Returns:
            Provider instance or None if creation fails
        """
        if provider_type not in cls._providers:
            logger.error(f"❌ Unknown provider type: {provider_type}")
            logger.info(f"📋 Available providers: {list(cls._providers.keys())}")
            return None
        
        try:
            provider_class = cls._providers[provider_type]
            provider = provider_class(config)
            
            if provider.is_available():
                logger.info(f"✅ {provider_type} provider created and available")
                return provider
            else:
                logger.warning(f"⚠️ {provider_type} provider created but not available")
                return provider  # Return anyway, might be useful for diagnostics
                
        except Exception as e:
            logger.error(f"❌ Failed to create {provider_type} provider: {str(e)}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Type[BaseLLMProvider]]:
        """
        Get dictionary of available provider types and their classes
        
        Returns:
            Dict mapping provider names to provider classes
        """
        return cls._providers.copy()
    
    @classmethod
    def register_provider(
        cls, 
        provider_type: str, 
        provider_class: Type[BaseLLMProvider]
    ) -> None:
        """
        Register a new provider type
        
        Args:
            provider_type: Name of the provider type
            provider_class: Provider class to register
        """
        if not issubclass(provider_class, (BaseLLMProvider, BaseImageProvider)):
            raise ValueError(f"Provider class must inherit from BaseLLMProvider or BaseImageProvider")
        
        cls._providers[provider_type] = provider_class
        logger.info(f"📝 Registered new provider: {provider_type}")
    
    @classmethod
    def create_multiple_providers(
        cls, 
        providers_config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, BaseLLMProvider]:
        """
        Create multiple providers from configuration
        
        Args:
            providers_config: Dict mapping provider names to their configs
            
        Returns:
            Dict of successfully created providers
        """
        providers = {}
        
        for name, config in providers_config.items():
            provider_type = config.get('type')
            if not provider_type:
                logger.error(f"❌ No provider type specified for {name}")
                continue
            
            provider = cls.create_provider(provider_type, config)
            if provider:
                providers[name] = provider
                logger.info(f"✅ Provider '{name}' ({provider_type}) created successfully")
            else:
                logger.error(f"❌ Failed to create provider '{name}' ({provider_type})")
        
        logger.info(f"🎯 Created {len(providers)} out of {len(providers_config)} providers")
        return providers

    @classmethod
    def get_fallback_provider(cls, provider_configs: Dict[str, Dict[str, Any]], fallback_type: str = "openai") -> Optional[BaseLLMProvider]:
        """
        Get a fallback provider for error cases
        
        Args:
            provider_configs: Provider configurations
            fallback_type: Preferred fallback provider type
            
        Returns:
            Fallback provider instance or None
        """
        # Try the specified fallback first
        if fallback_type in provider_configs:
            provider = cls.create_provider(fallback_type, provider_configs[fallback_type])
            if provider and provider.is_available():
                logger.info(f"✅ Using {fallback_type} as fallback provider")
                return provider
        
        # Try any available provider
        for provider_type, config in provider_configs.items():
            provider = cls.create_provider(provider_type, config)
            if provider and provider.is_available():
                logger.info(f"✅ Using {provider_type} as fallback provider")
                return provider
        
        logger.error("❌ No fallback provider available")
        return None
    
    @classmethod
    def _load_provider(cls, provider_type: str):
        """Lazy load a provider class"""
        if provider_type not in cls._lazy_providers:
            return
        
        module_name, class_name = cls._lazy_providers[provider_type]
        
        try:
            # Import the module dynamically
            import importlib
            module = importlib.import_module(f"providers.{module_name}")
            provider_class = getattr(module, class_name)
            
            # Register the provider
            cls._providers[provider_type] = provider_class
            logger.info(f"✅ Lazy loaded provider: {provider_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to lazy load {provider_type} provider: {str(e)}")
            logger.warning(f"⚠️ {provider_type} provider will not be available") 