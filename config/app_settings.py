"""
Centralized Application Settings and Configuration Management
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


def load_pipeline_config() -> Dict[str, Any]:
    """Load configuration from pipeline.yaml file"""
    config_path = Path(__file__).parent / 'pipeline.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Expand environment variables in the config
            config = expand_env_vars(config)
            logger.info(f"✅ Loaded pipeline configuration from {config_path}")
            return config.get('environment', {})
    except Exception as e:
        logger.warning(f"⚠️ Failed to load pipeline configuration: {str(e)}")
        return {}


def expand_env_vars(obj):
    """Recursively expand environment variables in config values"""
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        env_var = obj[2:-1]
        return os.environ.get(env_var, '')
    else:
        return obj


# Load pipeline config at module level
_pipeline_config = load_pipeline_config()


def get_config_value(env_key: str, pipeline_path: str, default: str = '') -> str:
    """Get configuration value from environment or pipeline config with fallback"""
    # First try environment variable
    env_value = os.environ.get(env_key)
    if env_value:
        return str(env_value)
    
    # Then try pipeline config
    try:
        keys = pipeline_path.split('.')
        value = _pipeline_config
        for key in keys:
            value = value[key]
        # Ensure we always return a string
        return str(value) if value is not None else default
    except (KeyError, TypeError):
        return default


@dataclass
class BlogSettings:
    """Blog-specific configuration settings"""
    
    # Domain and URLs
    domain: str = field(default_factory=lambda: get_config_value('BLOG_DOMAIN', 'blog.domain', 'braincargo.com'))
    cdn_base_url: str = field(default_factory=lambda: get_config_value('CDN_BASE_URL', 'media.cdn_base_url', 'https://braincargo.com'))
    
    # Content settings
    default_author: str = field(default_factory=lambda: get_config_value('BLOG_DEFAULT_AUTHOR', 'blog.default_author', 'AI Assistant'))
    default_category: str = field(default_factory=lambda: get_config_value('BLOG_DEFAULT_CATEGORY', 'blog.default_category', 'Technology'))
    call_to_action: str = field(default_factory=lambda: get_config_value('BLOG_CALL_TO_ACTION', 'blog.call_to_action', 'Join the Internet of Value & Freedom at braincargo.com'))
    
    # Company/Brand settings
    company_name: str = field(default_factory=lambda: get_config_value('COMPANY_NAME', 'blog.company_name', 'BrainCargo LLC'))
    service_name: str = field(default_factory=lambda: get_config_value('SERVICE_NAME', 'blog.service_name', 'Brain Blog Service'))
    
    # Media settings
    media_prefix: str = field(default_factory=lambda: get_config_value('MEDIA_PREFIX', 'media.prefix', 'media'))
    
    def get_blog_url(self, slug: str, post_id: str) -> str:
        """Generate blog post URL"""
        return f"https://{self.domain}/blog/{slug}/{post_id}"
    
    def get_blog_index_url(self) -> str:
        """Generate blog index API URL"""
        return f"https://{self.domain}/blog/api/blog-index.json"
    
    def get_media_url(self, s3_key: str) -> str:
        """Generate media URL"""
        return f"{self.cdn_base_url}/{s3_key}"


@dataclass
class SecuritySettings:
    """Security-related configuration settings"""
    
    authorized_phone_number: str = field(default_factory=lambda: get_config_value('AUTHORIZED_PHONE_NUMBER', 'security.authorized_phone_number', ''))
    twilio_auth_token: str = field(default_factory=lambda: get_config_value('TWILIO_AUTH_TOKEN', 'security.twilio_auth_token', ''))
    api_key_required: bool = field(default_factory=lambda: get_config_value('API_KEY_REQUIRED', 'security.api_key_required', 'true').lower() == 'true')
    max_request_size: int = field(default_factory=lambda: int(get_config_value('MAX_REQUEST_SIZE', 'security.max_request_size', '16777216')))  # 16MB
    rate_limit_enabled: bool = field(default_factory=lambda: get_config_value('RATE_LIMIT_ENABLED', 'security.rate_limit_enabled', 'true').lower() == 'true')
    webhook_signature_validation: bool = field(default_factory=lambda: get_config_value('WEBHOOK_SIGNATURE_VALIDATION', 'security.webhook_signature_validation', 'true').lower() == 'true')
    
    def is_phone_authorized(self, phone_number: str) -> bool:
        """Check if phone number is authorized - STRICT VALIDATION"""
        if not self.authorized_phone_number:
            logger.error("❌ AUTHORIZED_PHONE_NUMBER not configured - denying access")
            return False
        
        # Clean phone numbers for comparison
        clean_incoming = ''.join(filter(str.isdigit, phone_number))
        clean_authorized = ''.join(filter(str.isdigit, self.authorized_phone_number))
        
        # Require exact match of last 10 digits (US phone number format)
        if len(clean_authorized) >= 10:
            authorized_suffix = clean_authorized[-10:]
            incoming_suffix = clean_incoming[-10:] if len(clean_incoming) >= 10 else clean_incoming
            is_authorized = authorized_suffix == incoming_suffix
        else:
            # Fallback to full number match for international numbers
            is_authorized = clean_incoming == clean_authorized
        
        if not is_authorized:
            logger.warning(f"🚫 Phone authorization failed: {clean_incoming[-4:]}*** vs {clean_authorized[-4:]}***")
        
        return is_authorized
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validate API key for programmatic access"""
        expected_key = os.environ.get('API_ACCESS_KEY')
        if not expected_key:
            logger.warning("API_ACCESS_KEY not configured")
            return False
        
        # Use constant-time comparison to prevent timing attacks
        import hmac
        return hmac.compare_digest(provided_key, expected_key)


@dataclass
class APISettings:
    """API and service configuration settings"""
    
    # OpenAI settings
    openai_api_key: str = field(default_factory=lambda: get_config_value('OPENAI_API_KEY', 'api_keys.openai', ''))
    vector_store_id: str = field(default_factory=lambda: os.environ.get('OPENAI_VECTOR_STORE_ID', ''))
    
    # Anthropic settings
    anthropic_api_key: str = field(default_factory=lambda: get_config_value('ANTHROPIC_API_KEY', 'api_keys.anthropic', ''))
    
    # Grok settings
    grok_api_key: str = field(default_factory=lambda: get_config_value('GROK_API_KEY', 'api_keys.grok', ''))
    
    # Gemini settings
    gemini_api_key: str = field(default_factory=lambda: get_config_value('GEMINI_API_KEY', 'api_keys.gemini', ''))
    
    # AWS settings
    aws_access_key: str = field(default_factory=lambda: get_config_value('AWS_ACCESS_KEY_ID', 'aws.access_key_id', ''))
    aws_secret_key: str = field(default_factory=lambda: get_config_value('AWS_SECRET_ACCESS_KEY', 'aws.secret_access_key', ''))
    aws_region: str = field(default_factory=lambda: get_config_value('AWS_DEFAULT_REGION', 'aws.region', 'us-west-2'))
    
    # S3 settings
    blog_posts_bucket: str = field(default_factory=lambda: get_config_value('BLOG_POSTS_BUCKET', 'aws.bucket_name', ''))
    
    def validate_required_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present"""
        return {
            'openai': bool(self.openai_api_key),
            'anthropic': bool(self.anthropic_api_key),
            'grok': bool(self.grok_api_key),
            'gemini': bool(self.gemini_api_key),
            'aws_configured': bool(self.aws_access_key and self.aws_secret_key),
            's3_configured': bool(self.blog_posts_bucket),
            'phone_configured': bool(os.environ.get('AUTHORIZED_PHONE_NUMBER'))
        }
    
    def get_available_providers(self) -> list[str]:
        """Get list of providers with valid API keys"""
        available = []
        if self.openai_api_key:
            available.append('openai')
        if self.anthropic_api_key:
            available.append('anthropic')
        if self.grok_api_key:
            available.append('grok')
        if self.gemini_api_key:
            available.append('gemini')
        return available


@dataclass
class AppSettings:
    """Main application settings container"""
    
    blog: BlogSettings = field(default_factory=BlogSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    api: APISettings = field(default_factory=APISettings)
    
    # Application settings
    debug: bool = field(default_factory=lambda: get_config_value('DEBUG', 'app.debug', 'false').lower() == 'true')
    port: int = field(default_factory=lambda: int(get_config_value('PORT', 'app.port', '8080')))
    log_level: str = field(default_factory=lambda: get_config_value('LOG_LEVEL', 'app.log_level', 'INFO'))
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate application configuration and return status"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'security_issues': [],
            'api_status': self.api.validate_required_keys()
        }
        
        # Check critical security settings
        if not self.security.authorized_phone_number:
            validation['errors'].append('AUTHORIZED_PHONE_NUMBER not configured - webhook will be disabled')
            validation['valid'] = False
        
        # Check for debug mode in production
        if self.debug and os.environ.get('ENVIRONMENT', 'production').lower() == 'production':
            validation['security_issues'].append('DEBUG mode enabled in production environment')
        
        # Check that at least one AI provider is available
        available_providers = self.api.get_available_providers()
        if not available_providers:
            validation['errors'].append('No AI provider API keys configured (need at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GROK_API_KEY, GEMINI_API_KEY)')
            validation['valid'] = False
        else:
            validation['info'] = f"Available AI providers: {', '.join(available_providers)}"
        
        # Check optional but recommended settings
        if not self.api.blog_posts_bucket:
            validation['warnings'].append('BLOG_POSTS_BUCKET not configured - S3 storage disabled')
        
        if self.blog.domain == 'braincargo.com':
            validation['warnings'].append('BLOG_DOMAIN not configured - using placeholder')
        
        # Security recommendations
        if not os.environ.get('API_ACCESS_KEY'):
            validation['warnings'].append('API_ACCESS_KEY not configured - programmatic API access disabled')
        
        # Critical: Check Twilio webhook signature validation
        if not self.security.twilio_auth_token:
            validation['security_issues'].append('TWILIO_AUTH_TOKEN not configured - webhook vulnerable to spoofing attacks')
            validation['valid'] = False
        
        if not self.security.webhook_signature_validation:
            validation['security_issues'].append('Webhook signature validation disabled - spoofing attacks possible')
        
        return validation
    
    def get_runtime_info(self) -> Dict[str, Any]:
        """Get runtime configuration information (safe for logging)"""
        return {
            'service_name': self.blog.service_name,
            'company_name': self.blog.company_name,
            'domain': self.blog.domain,
            'debug': self.debug,
            'port': self.port,
            'api_keys_configured': {
                'openai': bool(self.api.openai_api_key),
                'anthropic': bool(self.api.anthropic_api_key),
                'grok': bool(self.api.grok_api_key),
                'gemini': bool(self.api.gemini_api_key),
                'aws': bool(self.api.aws_access_key),
            },
            's3_bucket': self.api.blog_posts_bucket or 'not_configured',
            'media_prefix': self.blog.media_prefix
        }


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get global application settings instance"""
    global _settings
    if _settings is None:
        _settings = AppSettings()
        logger.info("⚙️ Application settings initialized")
    return _settings


def reload_settings() -> AppSettings:
    """Reload settings from environment variables"""
    global _settings
    _settings = AppSettings()
    logger.info("🔄 Application settings reloaded")
    return _settings


# Convenience functions for common settings
def get_blog_settings() -> BlogSettings:
    """Get blog-specific settings"""
    return get_settings().blog


def get_security_settings() -> SecuritySettings:
    """Get security-specific settings"""
    return get_settings().security


def get_api_settings() -> APISettings:
    """Get API-specific settings"""
    return get_settings().api 
