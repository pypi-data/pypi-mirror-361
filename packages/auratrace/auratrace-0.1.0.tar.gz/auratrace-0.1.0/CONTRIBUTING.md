# Contributing to AuraTrace

Thank you for your interest in contributing to AuraTrace! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions from the community! Here are the main ways you can contribute:

### 🐛 **Report Bugs**
- Use [GitHub Issues](https://github.com/Cosmos-Coder-Ray/AuraTrace.git/issues)
- Include detailed reproduction steps
- Provide error messages and stack traces
- Mention your environment (OS, Python version, etc.)

### 💡 **Suggest Features**
- Start a [GitHub Discussion](https://github.com/Cosmos-Coder-Ray/AuraTrace.git/discussions)
- Describe the use case and benefits
- Include mockups or examples if possible

### 📝 **Improve Documentation**
- Fix typos and clarify unclear sections
- Add missing examples or tutorials
- Improve API documentation
- Translate documentation to other languages

### 🔧 **Fix Bugs**
- Look for issues labeled "good first issue"
- Comment on the issue before starting work
- Follow the coding guidelines below
- Include tests for your fixes

### 🚀 **Add Features**
- Discuss the feature in an issue first
- Create a detailed design proposal
- Implement with comprehensive tests
- Update documentation

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip or conda

### Local Development

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/Cosmos-Coder-Ray/AuraTrace.git
   cd auratrace
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**
   ```bash
   pytest
   ```

5. **Run linting**
   ```bash
   black auratrace tests
   flake8 auratrace tests
   mypy auratrace
   ```

## 📋 Pull Request Guidelines

### Before Submitting

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run the test suite**
   ```bash
   pytest
   ```

4. **Check code quality**
   ```bash
   black auratrace tests
   flake8 auratrace tests
   mypy auratrace
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Template

When creating a PR, use this template:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Added tests for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings for new functions
- [ ] Updated README if needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No breaking changes (or documented)
- [ ] Added appropriate labels
```

## 📝 Code Style Guidelines

### Python Code

We use the following tools for code quality:

- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking

### Code Style Rules

1. **Follow PEP 8** - Use Black for automatic formatting
2. **Type hints** - Use type hints for all function parameters and return values
3. **Docstrings** - Use Google-style docstrings
4. **Naming** - Use descriptive names, follow Python conventions
5. **Imports** - Group imports: standard library, third-party, local

### Example

```python
from typing import List, Optional, Dict
import pandas as pd
from auratrace.core.tracer import Tracer


def process_dataframe(
    df: pd.DataFrame, 
    operations: List[str], 
    config: Optional[Dict] = None
) -> pd.DataFrame:
    """Process a dataframe with specified operations.
    
    Args:
        df: Input dataframe to process
        operations: List of operations to apply
        config: Optional configuration dictionary
        
    Returns:
        Processed dataframe
        
    Raises:
        ValueError: If operations list is empty
    """
    if not operations:
        raise ValueError("Operations list cannot be empty")
    
    # Your implementation here
    return df
```

## 🧪 Testing Guidelines

### Test Structure

- Place tests in the `tests/` directory
- Mirror the package structure
- Use descriptive test names
- Group related tests in classes

### Test Requirements

- **Coverage**: Aim for >90% code coverage
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **Edge cases**: Test error conditions and edge cases

### Example Test

```python
import pytest
import pandas as pd
from auratrace.core.tracer import Tracer


class TestTracer:
    """Test cases for the Tracer class."""
    
    def test_tracer_initialization(self):
        """Test tracer initialization."""
        tracer = Tracer()
        assert tracer is not None
        assert len(tracer.operations) == 0
    
    def test_trace_dataframe_creation(self):
        """Test tracing dataframe creation."""
        tracer = Tracer()
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        # Your test implementation
        assert len(tracer.dataframes) == 1
```

## 📚 Documentation Guidelines

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of what the function does.
    
    Longer description if needed, explaining the function's purpose,
    behavior, and usage.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> function_name("test", 42)
        True
    """
```

### README Updates

When adding features, update:
- Main README.md if it's a user-facing feature
- Relevant documentation files
- Example scripts if applicable

## 🏷️ Issue Labels

We use the following labels:

- **bug** - Something isn't working
- **enhancement** - New feature or request
- **documentation** - Improvements to documentation
- **good first issue** - Good for newcomers
- **help wanted** - Extra attention is needed
- **priority: high** - High priority issues
- **priority: low** - Low priority issues
- **wontfix** - Will not be fixed

## 🚀 Release Process

### For Contributors

1. **Create a feature branch** from `main`
2. **Make your changes** following guidelines
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Submit a PR** with detailed description
6. **Address review comments** promptly

### For Maintainers

1. **Review PRs** thoroughly
2. **Run CI checks** before merging
3. **Squash commits** when merging
4. **Update CHANGELOG.md** for releases
5. **Create releases** with proper tags

## 🎯 Areas for Contribution

### High Priority

- **Performance improvements** - Optimize memory usage and execution time
- **Additional data sources** - Support for more data formats
- **Enhanced visualization** - Better graphs and dashboards
- **Quality rules** - More built-in quality checks

### Medium Priority

- **Documentation** - More examples and tutorials
- **Testing** - Improve test coverage
- **CLI improvements** - Better user experience
- **Configuration** - More flexible configuration options

### Low Priority

- **Translations** - Documentation in other languages
- **Examples** - More real-world examples
- **Blog posts** - Tutorials and case studies

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please:

- **Be respectful** - Treat others with respect
- **Be collaborative** - Work together constructively
- **Be helpful** - Help others learn and grow
- **Be inclusive** - Welcome diverse perspectives

### Communication

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and ideas
- **Pull Requests** - For code contributions
- **Email** - For sensitive or private matters

## 📞 Getting Help

### For Contributors

- **Read the docs** - Check existing documentation
- **Search issues** - Look for similar problems
- **Ask in discussions** - Use GitHub Discussions
- **Join community** - Connect with other contributors

### For New Contributors

- Start with "good first issue" labels
- Ask questions in GitHub Discussions
- Review existing PRs to understand the process
- Don't hesitate to ask for help!



## 📄 License

By contributing to AuraTrace, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to AuraTrace! 🎉 