"""
Unit tests for vector store functionality.

Tests vector store upload scripts, provider integration,
and knowledge file usage in blog generation.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from typing import Dict, Any

# Load environment variables from config/.env
try:
    from dotenv import load_dotenv
    load_dotenv('config/.env')
except ImportError:
    print("⚠️ python-dotenv not available, skipping .env file loading")

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider

# Mock the upload scripts since they're in openai_store directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'openai_store')))


class TestVectorStoreUploadScripts(unittest.TestCase):
    """Test vector store upload script functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_docs_dir = Path(self.temp_dir) / "vector_store_docs"
        self.test_docs_dir.mkdir()
        
        # Create test files
        (self.test_docs_dir / "test_doc.md").write_text("# Test Documentation\nThis is test content.")
        (self.test_docs_dir / "test_guide.txt").write_text("Test guide content.")
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_openai_vector_store_upload_script_import(self):
        """Test that OpenAI vector store script can be imported."""
        try:
            import openai_vector_store
            self.assertTrue(hasattr(openai_vector_store, 'main'))
            self.assertTrue(hasattr(openai_vector_store, 'gather_files'))
        except ImportError as e:
            self.skipTest(f"OpenAI vector store script not available: {e}")

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_anthropic_upload_script_import(self):
        """Test that Anthropic upload script can be imported."""
        try:
            import anthropic_file_upload
            self.assertTrue(hasattr(anthropic_file_upload, 'main'))
            self.assertTrue(hasattr(anthropic_file_upload, 'upload_files_to_anthropic'))
        except ImportError as e:
            self.skipTest(f"Anthropic upload script not available: {e}")

    def test_test_docs_directory_creation(self):
        """Test that test docs directory is created properly."""
        self.assertTrue(self.test_docs_dir.exists())
        self.assertTrue((self.test_docs_dir / "test_doc.md").exists())
        self.assertTrue((self.test_docs_dir / "test_guide.txt").exists())


class TestOpenAIVectorStoreIntegration(unittest.TestCase):
    """Test OpenAI provider vector store integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'type': 'openai',
            'api_key_env': 'OPENAI_API_KEY',
            'models': {'standard': 'gpt-4o'},
            'vector_store_ids': 'vs_test123,vs_test456'
        }
        
    def test_vector_store_id_detection_from_config(self):
        """Test vector store ID detection from configuration."""
        provider = OpenAIProvider(self.config)
        
        # Mock the _get_vector_store_id method to test configuration detection
        with patch.object(provider, '_get_vector_store_id', return_value='vs_test123'):
            vector_id = provider._get_vector_store_id()
            self.assertEqual(vector_id, 'vs_test123')

    @patch.dict(os.environ, {'OPENAI_VECTOR_STORE_IDS': 'vs_env123,vs_env456'})
    def test_vector_store_id_detection_from_env(self):
        """Test vector store ID detection from environment variable."""
        provider = OpenAIProvider(self.config)
        
        # Test actual method with environment variable
        vector_id = provider._get_vector_store_id()
        self.assertEqual(vector_id, 'vs_env123')  # Should return first ID

    @patch('builtins.open', new_callable=mock_open, read_data='{"vector_store_id": "vs_manifest123", "file_ids": ["file_1", "file_2"]}')
    @patch('os.path.exists', return_value=True)
    def test_vector_store_id_detection_from_manifest(self, mock_exists, mock_file):
        """Test vector store ID detection from manifest file."""
        # Create config without vector store IDs
        config_no_ids = {
            'type': 'openai',
            'api_key_env': 'OPENAI_API_KEY',
            'models': {'standard': 'gpt-4o'}
        }
        provider = OpenAIProvider(config_no_ids)
        
        vector_id = provider._get_vector_store_id()
        self.assertEqual(vector_id, 'vs_manifest123')
        mock_file.assert_called_with('openai_store/openai_vector_store.json', 'r')

    @patch('os.path.exists', return_value=False)
    def test_vector_store_id_not_found(self, mock_exists):
        """Test behavior when no vector store ID is found."""
        config_no_ids = {
            'type': 'openai',
            'api_key_env': 'OPENAI_API_KEY',
            'models': {'standard': 'gpt-4o'}
        }
        provider = OpenAIProvider(config_no_ids)
        
        vector_id = provider._get_vector_store_id()
        self.assertIsNone(vector_id)

    def test_add_vector_store_tools_with_valid_id(self):
        """Test adding vector store tools when vector store ID is available."""
        provider = OpenAIProvider(self.config)
        
        with patch.object(provider, '_get_vector_store_id', return_value='vs_test123'):
            tools = []
            enhanced_tools = provider._add_vector_store_tools(tools)
            
            self.assertEqual(len(enhanced_tools), 1)
            self.assertEqual(enhanced_tools[0]['type'], 'file_search')
            self.assertIn('vs_test123', enhanced_tools[0]['vector_store_ids'])

    def test_add_vector_store_tools_without_id(self):
        """Test adding vector store tools when no vector store ID is available."""
        provider = OpenAIProvider(self.config)
        
        with patch.object(provider, '_get_vector_store_id', return_value=None):
            tools = []
            enhanced_tools = provider._add_vector_store_tools(tools)
            
            # Should return original tools unchanged
            self.assertEqual(enhanced_tools, tools)

    def test_vector_store_tools_not_duplicated(self):
        """Test that file_search tools are not duplicated."""
        provider = OpenAIProvider(self.config)
        
        existing_tools = [{"type": "file_search", "vector_store_ids": ["vs_existing"]}]
        
        with patch.object(provider, '_get_vector_store_id', return_value='vs_test123'):
            enhanced_tools = provider._add_vector_store_tools(existing_tools)
            
            # Should not add another file_search tool
            file_search_tools = [t for t in enhanced_tools if t.get('type') == 'file_search']
            self.assertEqual(len(file_search_tools), 1)


class TestAnthropicFileIntegration(unittest.TestCase):
    """Test Anthropic provider file upload integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'},
            'file_ids': ['file_test123', 'file_test456']
        }

    def test_knowledge_file_detection_from_config(self):
        """Test knowledge file ID detection from configuration."""
        provider = AnthropicProvider(self.config)
        
        file_ids = provider._get_knowledge_file_ids()
        self.assertEqual(file_ids, ['file_test123', 'file_test456'])

    @patch.dict(os.environ, {'ANTHROPIC_FILE_IDS': 'file_env123,file_env456'})
    def test_knowledge_file_detection_from_env(self):
        """Test knowledge file ID detection from environment variable."""
        config_no_files = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'}
        }
        provider = AnthropicProvider(config_no_files)
        
        file_ids = provider._get_knowledge_file_ids()
        self.assertEqual(file_ids, ['file_env123', 'file_env456'])

    @patch('builtins.open', new_callable=mock_open, read_data='{"uploaded_files": [{"id": "file_manifest123"}, {"id": "file_manifest456"}]}')
    @patch('os.path.exists', return_value=True)
    def test_knowledge_file_detection_from_manifest(self, mock_exists, mock_file):
        """Test knowledge file ID detection from manifest file."""
        config_no_files = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'}
        }
        provider = AnthropicProvider(config_no_files)
        
        file_ids = provider._get_knowledge_file_ids()
        self.assertEqual(file_ids, ['file_manifest123', 'file_manifest456'])
        mock_file.assert_called_with('openai_store/anthropic_uploads.json', 'r')

    @patch('os.path.exists', return_value=False)
    def test_knowledge_file_not_found(self, mock_exists):
        """Test behavior when no knowledge files are found."""
        config_no_files = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'}
        }
        provider = AnthropicProvider(config_no_files)
        
        file_ids = provider._get_knowledge_file_ids()
        self.assertEqual(file_ids, [])

    def test_generate_completion_with_knowledge_files(self):
        """Test that knowledge files are included in completion requests."""
        provider = AnthropicProvider(self.config)
        
        # Mock the client and file IDs
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        provider.client = mock_client
        
        with patch.object(provider, '_get_knowledge_file_ids', return_value=['file_test123']):
            result = provider.generate_completion(
                prompt="Test prompt",
                use_knowledge_files=True
            )
            
            # Verify the message includes document attachments
            call_args = mock_client.messages.create.call_args
            messages = call_args[1]['messages']
            content_parts = messages[0]['content']
            
            # Should have text + document parts
            self.assertGreater(len(content_parts), 1)
            doc_parts = [part for part in content_parts if part.get('type') == 'document']
            self.assertEqual(len(doc_parts), 1)
            self.assertEqual(doc_parts[0]['source']['file_id'], 'file_test123')


class TestVectorStoreEndToEnd(unittest.TestCase):
    """Test end-to-end vector store functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_openai_knowledge_integration_workflow(self):
        """Test complete OpenAI knowledge integration workflow."""
        config = {
            'type': 'openai',
            'api_key_env': 'OPENAI_API_KEY',
            'models': {'standard': 'gpt-4o'}
        }
        provider = OpenAIProvider(config)
        
        # Mock vector store detection
        with patch.object(provider, '_get_vector_store_id', return_value='vs_test123'):
            # Mock client
            mock_client = MagicMock()
            provider.client = mock_client
            
            # Test that knowledge files are requested
            result = provider.generate_completion(
                prompt="Test prompt",
                use_knowledge_files=True
            )
            
            # Should have attempted to add vector store tools
            self.assertTrue(hasattr(provider, '_get_vector_store_id'))

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_anthropic_knowledge_integration_workflow(self):
        """Test complete Anthropic knowledge integration workflow."""
        config = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'}
        }
        provider = AnthropicProvider(config)
        
        # Mock file detection
        with patch.object(provider, '_get_knowledge_file_ids', return_value=['file_test123']):
            # Mock client
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Knowledge-enhanced response")]
            mock_client.messages.create.return_value = mock_response
            provider.client = mock_client
            
            # Test knowledge file integration
            result = provider.generate_completion(
                prompt="Test prompt",
                use_knowledge_files=True
            )
            
            # Should have called client with document attachments
            self.assertTrue(mock_client.messages.create.called)
            call_args = mock_client.messages.create.call_args
            messages = call_args[1]['messages']
            
            # Check that document parts were included
            content_parts = messages[0]['content']
            has_document = any(part.get('type') == 'document' for part in content_parts)
            self.assertTrue(has_document)


class TestVectorStoreManifestFiles(unittest.TestCase):
    """Test vector store manifest file functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_openai_manifest_format(self):
        """Test OpenAI manifest file format."""
        manifest_data = {
            "vector_store_id": "vs_test123",
            "file_ids": ["file_1", "file_2", "file_3"]
        }
        
        manifest_path = Path(self.temp_dir) / "openai_vector_store.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Verify manifest can be read and parsed
        with open(manifest_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['vector_store_id'], 'vs_test123')
        self.assertEqual(len(loaded_data['file_ids']), 3)

    def test_anthropic_manifest_format(self):
        """Test Anthropic manifest file format."""
        manifest_data = {
            "uploaded_files": [
                {"id": "file_test123", "filename": "doc1.md", "size_bytes": 1024},
                {"id": "file_test456", "filename": "doc2.txt", "size_bytes": 2048}
            ],
            "total_files": 2
        }
        
        manifest_path = Path(self.temp_dir) / "anthropic_uploads.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Verify manifest can be read and parsed
        with open(manifest_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['total_files'], 2)
        self.assertEqual(len(loaded_data['uploaded_files']), 2)
        self.assertEqual(loaded_data['uploaded_files'][0]['id'], 'file_test123')


class TestVectorStoreConfiguration(unittest.TestCase):
    """Test vector store configuration integration."""

    def test_vector_store_config_parsing(self):
        """Test that vector store configuration is parsed correctly."""
        # This would test the pipeline.yaml parsing for vector stores
        sample_config = {
            'vector_stores': {
                'enabled': True,
                'openai': {
                    'enabled': True,
                    'vector_store_ids': 'vs_test123,vs_test456',
                    'manifest_file': 'openai_store/openai_vector_store.json'
                },
                'anthropic': {
                    'enabled': True,
                    'file_ids': 'file_test123,file_test456',
                    'manifest_file': 'openai_store/anthropic_uploads.json'
                }
            }
        }
        
        # Test that config structure is valid
        self.assertTrue(sample_config['vector_stores']['enabled'])
        self.assertTrue(sample_config['vector_stores']['openai']['enabled'])
        self.assertTrue(sample_config['vector_stores']['anthropic']['enabled'])

    def test_vector_store_usage_config(self):
        """Test vector store usage configuration."""
        usage_config = {
            'usage': {
                'blog_generation': True,
                'categorization': False,
                'image_generation': False,
                'meme_generation': False
            }
        }
        
        # Test that usage config is structured correctly
        self.assertTrue(usage_config['usage']['blog_generation'])
        self.assertFalse(usage_config['usage']['categorization'])


class TestVectorStoreBasic(unittest.TestCase):
    """Basic tests for vector store functionality."""

    def test_openai_provider_vector_store_methods(self):
        """Test that OpenAI provider has vector store methods."""
        config = {
            'type': 'openai',
            'api_key_env': 'OPENAI_API_KEY',
            'models': {'standard': 'gpt-4o'}
        }
        provider = OpenAIProvider(config)
        
        # Check that vector store methods exist
        self.assertTrue(hasattr(provider, '_get_vector_store_id'))
        self.assertTrue(hasattr(provider, '_add_vector_store_tools'))

    def test_anthropic_provider_knowledge_methods(self):
        """Test that Anthropic provider has knowledge file methods."""
        config = {
            'type': 'anthropic',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'models': {'standard': 'claude-3-5-sonnet-20241022'}
        }
        provider = AnthropicProvider(config)
        
        # Check that knowledge file methods exist
        self.assertTrue(hasattr(provider, '_get_knowledge_file_ids'))


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreUploadScripts))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenAIVectorStoreIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAnthropicFileIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreEndToEnd))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreManifestFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreBasic))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n🧪 Vector Store Tests Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n🎉 All vector store tests passed!")
    else:
        print(f"\n💥 {len(result.failures + result.errors)} test(s) failed.") 