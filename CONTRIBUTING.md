# Contributing to Brain Blog Generator

Thank you for your interest in contributing to the Brain Blog Generator! This document provides guidelines and information for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- Docker (optional but recommended)
- At least one AI provider API key for testing

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/braincargo/brain-blog.git
   cd brain-blog
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment configuration**
   ```bash
   cp config/environment.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run tests to verify setup**
   ```bash
   python test_all.py
   ```

## 🔧 Development Guidelines

### Code Style

This project follows PEP 8 and uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all code quality checks:
```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

### Code Structure

```
brain-blog/
├── app.py                 # Main Flask application
├── config/               # Configuration management
├── pipeline/             # Blog generation pipeline
├── providers/            # AI provider implementations
├── prompts/              # AI prompts and templates
├── docs/                 # Documentation
├── tests/                # Test files
└── requirements*.txt     # Dependencies
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Type Hints

All new code should include type hints:

```python
from typing import Dict, List, Optional

def generate_blog(content: str, provider: str) -> Dict[str, Any]:
    """Generate a blog post using the specified provider."""
    pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python test_all.py

# Run specific test files
python test_blog_generation.py
python test_complete_pipeline.py

# Run with pytest (if available)
pytest
```

### Writing Tests

When adding new features, please include tests:

1. **Unit tests** for individual functions
2. **Integration tests** for complete workflows
3. **Provider tests** for AI provider integrations

Example test structure:
```python
import unittest
from unittest.mock import patch, MagicMock

class TestBlogGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_feature_functionality(self):
        """Test specific functionality."""
        # Test implementation
        pass
```

## 📝 Contributing Process

### 1. Choose an Issue

- Check the [Issues](https://github.com/braincargo/brain-blog/issues) page
- Look for issues labeled `good first issue` for beginners
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

```bash
git checkout -b feature/descriptive-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

- Follow the coding guidelines above
- Write or update tests as needed
- Update documentation if required
- Keep commits focused and atomic

### 4. Commit Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add support for Gemini AI provider"
git commit -m "Fix image generation timeout handling"
git commit -m "Update README with Docker setup instructions"

# Include issue number if applicable
git commit -m "Fix categorization logic (closes #123)"
```

### 5. Submit Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/descriptive-name
   ```

2. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Include a summary of changes
   - Add screenshots for UI changes

3. **Pull Request Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] All tests pass
   - [ ] New tests added (if applicable)
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

## 🔍 Areas for Contribution

### High Priority

- **New AI Providers**: Add support for additional AI services
- **Performance Improvements**: Optimize generation speed and resource usage
- **Error Handling**: Improve error messages and recovery
- **Documentation**: API docs, tutorials, examples

### Medium Priority

- **Image Generation**: Enhanced image generation features
- **Content Categorization**: Improved categorization algorithms
- **Testing**: Expand test coverage
- **Monitoring**: Better health checks and metrics

### Low Priority

- **UI Improvements**: Web interface enhancements
- **Storage Backends**: Additional storage options
- **Internationalization**: Multi-language support

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - Docker version (if using)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages/logs

3. **Additional Context**
   - Configuration details (without sensitive info)
   - Related issues or pull requests

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and their trade-offs

## 📚 Documentation

Help improve documentation:

- **API Documentation**: Document endpoints and parameters
- **Setup Guides**: Installation and configuration instructions
- **Tutorials**: Step-by-step usage examples
- **Code Comments**: Inline documentation for complex logic

## 🔐 Security

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. **Email** the maintainers directly
3. **Provide details** about the vulnerability
4. **Wait for response** before disclosing publicly

## 📋 Code Review Process

All contributions go through code review:

1. **Automated Checks**: CI/CD runs tests and quality checks
2. **Peer Review**: Maintainers review code for quality and fit
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, changes are merged

### Review Criteria

- **Functionality**: Code works as intended
- **Quality**: Follows style guidelines and best practices
- **Testing**: Adequate test coverage
- **Documentation**: Clear comments and docs
- **Impact**: Positive impact on the project

## 🎉 Recognition

Contributors are recognized in:

- **README**: Contributors section
- **Releases**: Change logs and credits
- **Issues**: Acknowledgments for bug reports and suggestions

## 📞 Getting Help

Need help contributing?

- **Documentation**: Check the `/docs` directory
- **Issues**: Search existing issues for answers
- **Discussions**: Start a discussion for general questions
- **Chat**: Join our community chat (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Brain Blog Generator! 🚀 