"""
Base LLM Provider Abstract Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration
        
        Args:
            config: Provider configuration from YAML
        """
        self.config = config
        self.provider_type = config.get('type')
        self.models = config.get('models', {})
        self.default_temperature = config.get('default_temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 4000)
        self.api_key_env = config.get('api_key_env')
        
        # Initialize the client
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client"""
        pass
    
    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        model: str = "standard",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        output_format: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the provider's API
        
        Args:
            prompt: The input prompt
            model: Model type to use (fast, standard, creative)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            output_format: Expected output format (text, json)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with 'content' key and optional metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured correctly"""
        pass
    
    def get_model_name(self, model_type: str) -> str:
        """
        Get the actual model name for a model type
        
        Args:
            model_type: Type of model (fast, standard, creative)
            
        Returns:
            Actual model name for the provider
        """
        return self.models.get(model_type, self.models.get('standard', 'gpt-4o'))
    
    def get_temperature(self, temperature: Optional[float] = None) -> float:
        """Get temperature value, using default if not provided"""
        return temperature if temperature is not None else self.default_temperature
    
    def get_max_tokens(self, max_tokens: Optional[int] = None) -> int:
        """Get max tokens value, using default if not provided"""
        return max_tokens if max_tokens is not None else self.max_tokens
    
    def validate_response(self, response: Any, expected_format: str) -> bool:
        """
        Validate that the response matches expected format
        
        Args:
            response: Provider response
            expected_format: Expected format (text, json)
            
        Returns:
            True if valid, False otherwise
        """
        if expected_format == "json":
            try:
                import json
                if isinstance(response, str):
                    json.loads(response)
                return True
            except (json.JSONDecodeError, TypeError):
                return False
        return True
    
    def __str__(self):
        """String representation of the provider"""
        return f"{self.__class__.__name__}({self.provider_type})"


class BaseImageProvider(ABC):
    """Abstract base class for image generation providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the image provider with configuration
        
        Args:
            config: Provider configuration from YAML
        """
        self.config = config
        self.provider_type = config.get('type')
        self.image_models = config.get('image_models', {})
        self.default_size = config.get('default_size', '1024x1024')
        self.default_quality = config.get('default_quality', 'standard')
        self.supported_sizes = config.get('supported_sizes', ['1024x1024'])
        self.api_key_env = config.get('api_key_env')
        
        # Initialize the client
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client"""
        pass
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image using the provider's API
        
        Args:
            prompt: The image generation prompt
            size: Image size (e.g., "1024x1024")
            quality: Image quality level
            style: Image style
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with 'image_url' key and optional metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured correctly"""
        pass
    
    def get_image_model_name(self, model_type: str = 'default') -> str:
        """
        Get the actual image model name for a model type
        
        Args:
            model_type: Type of model (default, advanced, etc.)
            
        Returns:
            Actual model name for the provider
        """
        return self.image_models.get(model_type, self.image_models.get('default', 'default'))
    
    def validate_size(self, size: str) -> str:
        """
        Validate and return supported size
        
        Args:
            size: Requested image size
            
        Returns:
            Valid size for this provider
        """
        if size in self.supported_sizes:
            return size
        
        logger.warning(f"Size {size} not supported by {self.provider_type}, using {self.default_size}")
        return self.default_size
    
    def __str__(self):
        """String representation of the provider"""
        return f"{self.__class__.__name__}({self.provider_type})"


class MultiModalProvider(BaseLLMProvider):
    """Base class for providers that support both LLM and image generation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the multi-modal provider
        
        Args:
            config: Provider configuration from YAML
        """
        super().__init__(config)
        
        # Image generation capabilities
        self.image_models = config.get('image_models', {})
        self.default_size = config.get('default_size', '1024x1024')
        self.default_quality = config.get('default_quality', 'standard')
        self.supported_sizes = config.get('supported_sizes', ['1024x1024'])
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image from prompt - must be implemented by multi-modal providers"""
        pass
    
    def get_image_model_name(self, model_type: str = 'default') -> str:
        """Get actual image model name from model type"""
        return self.image_models.get(model_type, self.image_models.get('default', 'default'))
    
    def validate_size(self, size: str) -> str:
        """Validate and return supported size"""
        if size in self.supported_sizes:
            return size
        
        logger.warning(f"Size {size} not supported by {self.provider_type}, using {self.default_size}")
        return self.default_size 