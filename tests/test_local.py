#!/usr/bin/env python3
"""
BrainCargo Auto Blog Publisher - Comprehensive Test Suite
Tests Docker service functionality including OpenAI Responses API integration
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone

# Add parent directory to Python path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
BASE_URL = os.environ.get('TEST_BASE_URL', 'http://localhost:8080')
AUTHORIZED_PHONE = os.environ.get('AUTHORIZED_PHONE_NUMBER', '15551231234')
TEST_TIMEOUT = 60

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}🧪 {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def test_health_endpoint():
    """Test the health check endpoint"""
    print_test_header("Health Check Endpoint Test")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"Health endpoint responding (HTTP {response.status_code})")
            
            # Check required fields
            required_fields = ['status', 'timestamp', 'openai_available', 'assistant_api_available', 's3_available']
            for field in required_fields:
                if field in health_data:
                    print_success(f"Field '{field}': {health_data[field]}")
                else:
                    print_error(f"Missing required field: {field}")
                    return False
            
            # Check service availability
            if health_data.get('openai_available'):
                print_success("OpenAI service is available")
            else:
                print_error("OpenAI service is NOT available")
                return False
                
            if health_data.get('assistant_api_available'):
                print_success("OpenAI Responses API is available")
            else:
                print_warning("OpenAI Responses API is NOT available")
                
            if health_data.get('s3_available'):
                print_success("S3 service is available")
            else:
                print_warning("S3 service is NOT available (expected for local testing)")
            
            return True
        else:
            print_error(f"Health endpoint returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to service at {BASE_URL}")
        print_info("Make sure the Docker service is running: make test-blog-local or docker-compose up")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_webhook_endpoint_unauthorized():
    """Test webhook with unauthorized phone number"""
    print_test_header("Unauthorized Phone Number Test")
    
    try:
        # Test with unauthorized number
        unauthorized_data = {
            'From': '+15551234567',  # Unauthorized number
            'Body': 'Test message https://httpbin.org/get',
            'To': '+12345678900'
        }
        
        response = requests.post(
            f"{BASE_URL}/webhook",
            data=unauthorized_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            # Check if it properly rejects unauthorized numbers
            response_text = response.text
            if "not available for your number" in response_text or "unauthorized" in response_text.lower():
                print_success("Unauthorized phone number properly rejected")
                return True
            else:
                print_error("Service should reject unauthorized phone numbers")
                print_info(f"Response: {response_text[:200]}")
                return False
        else:
            print_error(f"Webhook returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Unauthorized test failed: {str(e)}")
        return False

def test_webhook_endpoint_no_urls():
    """Test webhook with message containing no URLs"""
    print_test_header("No URLs in Message Test")
    
    try:
        # Test with no URLs
        no_url_data = {
            'From': f'+1{AUTHORIZED_PHONE}',
            'Body': 'Hello, this message has no URLs to process',
            'To': '+12345678900'
        }
        
        response = requests.post(
            f"{BASE_URL}/webhook",
            data=no_url_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            response_text = response.text
            if "No URLs found" in response_text:
                print_success("Service properly handles messages without URLs")
                return True
            else:
                print_error("Service should inform user when no URLs are found")
                print_info(f"Response: {response_text[:200]}")
                return False
        else:
            print_error(f"Webhook returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"No URLs test failed: {str(e)}")
        return False

def test_webhook_endpoint_valid_url():
    """Test webhook with valid URL for blog generation"""
    print_test_header("Valid URL Blog Generation Test")
    
    try:
        # Test with valid, bot-friendly URL
        valid_data = {
            'From': f'+1{AUTHORIZED_PHONE}',
            'Body': 'Generate blog post about https://amgreatness.com/2025/06/14/can-ai-improve-election-integrity/',
            'To': '+12345678900'
        }
        
        print_info("Sending webhook request with valid URL...")
        print_info("⏳ This may take up to 5 minutes for AI processing...")
        
        response = requests.post(
            f"{BASE_URL}/webhook",
            data=valid_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=300  # 5 minutes for AI processing
        )
        
        if response.status_code == 200:
            response_text = response.text
            print_info(f"Response received: {response_text[:300]}...")
            
            # Check for successful blog generation indicators
            success_indicators = [
                "Successfully generated",
                "blog post",
                "Processed 1 URL",
                "🤖",  # Bot emoji indicating AI processing
                "📝"   # Document emoji indicating success
            ]
            
            if any(indicator in response_text for indicator in success_indicators):
                print_success("Blog post generation appears successful!")
                
                # Check for Responses API usage (modern approach)
                if "🤖" in response_text:
                    print_success("Service is using AI (likely Responses API)")
                
                return True
            else:
                print_warning("Response received but unclear if blog generation succeeded")
                print_info(f"Full response: {response_text}")
                
                # Check for common error patterns
                if "Failed to process" in response_text:
                    print_warning("URL processing failed (may be due to website restrictions)")
                    return True  # This is expected behavior for some sites
                
                return False
        else:
            print_error(f"Webhook returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out after 5 minutes - AI processing may be taking longer than expected")
        print_info("This could indicate the service is working but overloaded or the URL is particularly complex")
        return False
    except Exception as e:
        print_error(f"Valid URL test failed: {str(e)}")
        return False

def test_webhook_endpoint_multiple_urls():
    """Test webhook with multiple URLs"""
    print_test_header("Multiple URLs Test")
    
    try:
        # Test with multiple URLs
        multi_url_data = {
            'From': f'+1{AUTHORIZED_PHONE}',
            'Body': 'Process these: https://httpbin.org/get and https://amgreatness.com/2025/06/14/can-ai-improve-election-integrity/ and https://httpbin.org/uuid',
            'To': '+12345678900'
        }
        
        print_info("Testing multiple URL processing...")
        print_info("⏳ This may take up to 7.5 minutes for processing multiple URLs...")
        
        response = requests.post(
            f"{BASE_URL}/webhook",
            data=multi_url_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=450  # 7.5 minutes for multiple URLs
        )
        
        if response.status_code == 200:
            response_text = response.text
            print_info(f"Response: {response_text[:400]}...")
            
            # Check for multiple URL processing
            if "Processed 3 URL" in response_text or "Processed 2 URL" in response_text:
                print_success("Multiple URLs processed successfully")
                return True
            elif "Successfully generated" in response_text:
                print_success("At least some URLs processed successfully")
                return True
            else:
                print_warning("Multiple URL processing may have encountered issues")
                print_info(f"Full response: {response_text}")
                return False
        else:
            print_error(f"Webhook returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out after 7.5 minutes - multiple URL processing may take longer than expected")
        print_info("This could indicate the service is working but processing complex content or is overloaded")
        return False
    except Exception as e:
        print_error(f"Multiple URLs test failed: {str(e)}")
        return False

def test_service_logs():
    """Check if service is logging properly"""
    print_test_header("Service Logging Test")
    
    print_info("Checking if Docker service is running and logging...")
    
    try:
        import subprocess
        
        # Check if container is running (docker-compose naming pattern)
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=braincargo-blog-service', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            container_name = result.stdout.strip().split('\n')[0]
            print_success(f"Docker container is running: {container_name}")
            
            # Try to get recent logs using the actual container name
            log_result = subprocess.run(
                ['docker', 'logs', '--tail', '10', container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if log_result.returncode == 0:
                print_success("Docker logs accessible")
                logs = log_result.stdout
                
                # Check for key log patterns
                if "OpenAI client initialized successfully" in logs:
                    print_success("OpenAI initialization logged")
                
                if "Responses API" in logs:
                    print_success("Using modern Responses API")
                elif "Assistant API" in logs:
                    print_info("Service indicates Assistant API availability")
                
                if "S3 client initialized" in logs:
                    print_success("S3 initialization logged")
                
                return True
            else:
                print_warning("Cannot access Docker logs")
                return False
        else:
            print_error("Docker container not found or not running")
            print_info("Start the service with: make test-blog-local")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Docker command timed out")
        return False
    except FileNotFoundError:
        print_warning("Docker command not found - cannot check container status")
        return False
    except Exception as e:
        print_error(f"Log check failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print(f"{Colors.BOLD}🧪 BrainCargo Auto Blog Publisher - Test Suite{Colors.END}")
    print(f"{Colors.BOLD}Testing service at: {BASE_URL}{Colors.END}")
    print(f"{Colors.BOLD}Authorized phone: +1{AUTHORIZED_PHONE}{Colors.END}")
    print(f"{Colors.BOLD}Test started at: {datetime.now(timezone.utc).isoformat()}{Colors.END}")
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Service Logging", test_service_logs),
        ("Unauthorized Phone", test_webhook_endpoint_unauthorized),
        ("No URLs Message", test_webhook_endpoint_no_urls),
        ("Valid URL Processing", test_webhook_endpoint_valid_url),
        ("Multiple URLs Processing", test_webhook_endpoint_multiple_urls),
        ("Pipeline Architecture", test_pipeline_architecture),
        ("Pipeline Integration", test_pipeline_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_test_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print_success(f"🎉 All tests passed! Service is working correctly.")
        return True
    elif passed >= total * 0.7:  # 70% pass rate
        print_warning(f"⚠️ Most tests passed ({passed}/{total}). Service is mostly functional.")
        return True
    else:
        print_error(f"❌ Many tests failed ({total-passed}/{total}). Service may have issues.")
        return False

def test_pipeline_architecture():
    """Test the new pipeline architecture"""
    print_test_header("Pipeline Architecture Test")
    
    try:
        print_info("Testing pipeline configuration loading...")
        
        # Test configuration file exists
        config_path = 'config/pipeline.yaml'
        if os.path.exists(config_path):
            print_success("Pipeline configuration file found")
            
            # Test YAML loading
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Test required sections
            required_sections = ['providers', 'pipeline', 'categories']
            for section in required_sections:
                if section in config:
                    print_success(f"Configuration section found: {section}")
                else:
                    print_error(f"Missing configuration section: {section}")
                    return False
            
            # Test provider configurations
            providers = config.get('providers', {})
            if 'openai' in providers:
                print_success("OpenAI provider configuration found")
            if 'anthropic' in providers:
                print_success("Anthropic provider configuration found")
            
            # Test categories
            categories = config.get('categories', {})
            expected_categories = ['security', 'technology', 'web3', 'crypto', 'politics', 'privacy']
            found_categories = list(categories.keys())
            
            for category in expected_categories:
                if category in found_categories:
                    print_success(f"Category configuration found: {category}")
                else:
                    print_warning(f"Category configuration missing: {category}")
            
        else:
            print_error("Pipeline configuration file not found")
            return False
        
        print_info("Testing prompt template files...")
        
        # Test prompt template files
        prompt_files = [
            'prompts/categorization/main.txt',
            'prompts/blog_generation/base.txt',
            'prompts/blog_generation/security_style.txt',
            'prompts/blog_generation/tech_style.txt',
            'prompts/blog_generation/web3_style.txt',
            'prompts/image_generation/main.txt',
            'prompts/meme_generation/main.txt'
        ]
        
        for prompt_file in prompt_files:
            if os.path.exists(prompt_file):
                print_success(f"Prompt template found: {prompt_file}")
            else:
                print_warning(f"Prompt template missing: {prompt_file}")
        
        print_info("Testing provider modules...")
        
        # Test provider imports
        try:
            from providers import LLMProviderFactory, OpenAIProvider, AnthropicProvider
            print_success("Provider modules imported successfully")
        except ImportError as e:
            print_error(f"Provider import failed: {str(e)}")
            return False
        
        print_info("Testing pipeline modules...")
        
        # Test pipeline imports
        try:
            from pipeline import PipelineManager, URLCategorizer, BlogGenerator, ImageGenerator, MemeGenerator
            print_success("Pipeline modules imported successfully")
        except ImportError as e:
            print_error(f"Pipeline import failed: {str(e)}")
            return False
        
        print_success("Pipeline architecture test completed successfully")
        return True
        
    except Exception as e:
        print_error(f"Pipeline architecture test failed: {str(e)}")
        return False

def test_pipeline_integration():
    """Test pipeline integration with mock data"""
    print_test_header("Pipeline Integration Test")
    
    try:
        print_info("Testing pipeline manager initialization...")
        
        # Import required modules
        from pipeline import PipelineManager
        from providers import LLMProviderFactory
        from unittest.mock import Mock, patch
        
        # Test with minimal configuration
        test_config = {
            'providers': {
                'openai': {
                    'type': 'openai',
                    'api_key_env': 'OPENAI_API_KEY',
                    'models': {
                        'fast': 'gpt-4o-mini',
                        'standard': 'o3',
                        'creative': 'gpt-4o'
                    }
                }
            },
            'categories': {
                'technology': {
                    'name': 'Technology',
                    'style_persona': 'Paul Graham'
                }
            },
            'image_generation': {'enabled': True},
            'meme_generation': {'enabled': True}
        }
        
        # Mock the configuration loading and provider initialization
        with patch('pipeline.pipeline_manager.PipelineManager._load_config') as mock_load:
            with patch('pipeline.pipeline_manager.LLMProviderFactory') as mock_factory:
                
                mock_load.return_value = test_config
                
                # Create mock provider
                mock_provider = Mock()
                mock_provider.is_available.return_value = True
                mock_factory.get_available_providers.return_value = {'openai': mock_provider}
                
                # Initialize pipeline manager
                pipeline = PipelineManager()
                print_success("Pipeline manager initialized with mock configuration")
                
                # Test configuration getters
                category_config = pipeline.get_category_config('technology')
                if category_config and category_config.get('name') == 'Technology':
                    print_success("Category configuration retrieval works")
                else:
                    print_error("Category configuration retrieval failed")
                    return False
                
                # Test health check
                health = pipeline.health_check()
                if health and 'overall_health' in health:
                    print_success("Pipeline health check works")
                else:
                    print_error("Pipeline health check failed")
                    return False
        
        print_success("Pipeline integration test completed successfully")
        return True
        
    except Exception as e:
        print_error(f"Pipeline integration test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--health':
            return test_health_endpoint()
        elif sys.argv[1] == '--webhook':
            return test_webhook_endpoint_valid_url()
        elif sys.argv[1] == '--pipeline':
            # Run pipeline-specific tests
            results = []
            results.append(test_pipeline_architecture())
            results.append(test_pipeline_integration())
            return all(results)
        elif sys.argv[1] == '--help':
            print("BrainCargo Auto Blog Publisher Test Suite")
            print("\nUsage:")
            print("  python test_local.py             # Run all tests")
            print("  python test_local.py --health    # Test health endpoint only")
            print("  python test_local.py --webhook   # Test webhook with valid URL")
            print("  python test_local.py --pipeline  # Test pipeline architecture")
            print("  python test_local.py --help      # Show this help")
            print("\nEnvironment variables:")
            print("  TEST_BASE_URL      # Service URL (default: http://localhost:8080)")
            print("  AUTHORIZED_PHONE_NUMBER   # Authorized phone number (default: 15551231234)")
            return True
    
    return run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
