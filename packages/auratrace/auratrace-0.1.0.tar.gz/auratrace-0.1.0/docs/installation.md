# Installation Guide

This guide will help you install AuraTrace on your system. AuraTrace supports Python 3.8+ and works on Windows, macOS, and Linux.

## 📋 Prerequisites

Before installing AuraTrace, make sure you have:

- **Python 3.8 or higher** - Check with `python --version`
- **pip** (Python package installer) - Usually comes with Python
- **Git** (optional, for development) - For cloning the repository

## 🚀 Quick Installation

### Using pip (Recommended)

The easiest way to install AuraTrace is using pip:

```bash
pip install auratrace
```

### Using conda (Alternative)

If you prefer using conda:

```bash
conda install -c conda-forge auratrace
```

## 📦 Installation Options

### Basic Installation

Install the core package with essential dependencies:

```bash
pip install auratrace
```

### Full Installation (with all features)

Install with all optional dependencies for full functionality:

```bash
pip install auratrace[all]
```

### Development Installation

For development and contributing:

```bash
git clone https://github.com/auratrace/auratrace.git
cd auratrace
pip install -e .
```

## 🔧 Dependencies

AuraTrace has the following dependency categories:

### Core Dependencies
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `psutil` - System and process utilities
- `pyyaml` - YAML configuration files
- `typer` - CLI framework
- `rich` - Terminal formatting

### Optional Dependencies

#### AI Features
- `openai` - OpenAI API integration
- `langchain` - LangChain framework
- `chromadb` - Vector database for embeddings

#### Visualization
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization
- `plotly` - Interactive plots
- `pyvis` - Network visualization

#### Performance Monitoring
- `dask` - Parallel computing
- `pyarrow` - Arrow data format support

#### Testing and Development
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🐍 Virtual Environment (Recommended)

It's recommended to install AuraTrace in a virtual environment to avoid conflicts:

### Using venv (Python 3.3+)

```bash
# Create virtual environment
python -m venv auratrace_env

# Activate virtual environment
# On Windows:
auratrace_env\Scripts\activate
# On macOS/Linux:
source auratrace_env/bin/activate

# Install AuraTrace
pip install auratrace
```

### Using conda

```bash
# Create conda environment
conda create -n auratrace_env python=3.9

# Activate environment
conda activate auratrace_env

# Install AuraTrace
pip install auratrace
```

## 🤖 AI Assistant & LLM Providers (Optional)

AuraTrace's AI features are powered by pluggable LLM providers. You do **not** need to install any AI model or dependency unless you use AI features.

### Supported Providers
- **OpenAI** (e.g., GPT-3.5, GPT-4)
- **Hugging Face** (API or local models)
- **Custom API** (any HTTP endpoint)
- **Local Model** (user-supplied, e.g., transformers)
- **User-supplied Python function**

### Optional Dependencies
- `openai` (for OpenAI models)
- `transformers` (for Hugging Face/local models)
- `requests` (for custom API)

Install only what you need:

```bash
pip install auratrace[openai]        # For OpenAI
pip install auratrace[huggingface]   # For Hugging Face
pip install auratrace[all]           # For all AI features
```

### Configuring the AI Assistant

You can set the provider, model, and API key via environment variables or in code:

```bash
# Example: Use Hugging Face with a specific model
export AURATRACE_LLM_PROVIDER=huggingface
export AURATRACE_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Example: Use OpenAI
export AURATRACE_LLM_PROVIDER=openai
export AURATRACE_LLM_API_KEY=sk-...
export AURATRACE_LLM_MODEL=gpt-4
```

Or in Python:

```python
from auratrace.ai import AIAssistant
ai = AIAssistant(provider="huggingface", model="mistralai/Mistral-7B-Instruct-v0.2")
```

### First Use: Model Download/Setup
- If you run an AI command without the required model/dependency, AuraTrace will prompt you to install or configure it.
- You can change the default model/provider at any time.
- If you have your own LLM, you can use it by passing a custom function or API endpoint.

### Example: User-supplied LLM
```python
def my_llm(prompt):
    # Your custom logic
    return "My LLM response"
ai = AIAssistant(provider="user", custom_generate_fn=my_llm)
```

## 🔑 API Key Setup (Optional)

For AI-powered features, you'll need to set up API keys:

### OpenAI API Key

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
# On Windows:
set OPENAI_API_KEY=your_api_key_here

# On macOS/Linux:
export OPENAI_API_KEY=your_api_key_here
```

Or create a `.env` file in your project directory:

```
OPENAI_API_KEY=your_api_key_here
```

## ✅ Verification

After installation, verify that AuraTrace is working correctly:

### Check Installation

```bash
# Check if AuraTrace is installed
python -c "import auratrace; print('AuraTrace installed successfully!')"
```

### Test CLI

```bash
# Check CLI help
auratrace --help
```

### Run Quick Test

```bash
# Create a test script
echo "import pandas as pd; df = pd.DataFrame({'A': [1, 2, 3]}); print('Test successful')" > test.py

# Run with AuraTrace
auratrace run test.py
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors

If you get import errors, make sure all dependencies are installed:

```bash
pip install --upgrade auratrace
```

#### Permission Errors

On Linux/macOS, you might need to use `sudo`:

```bash
sudo pip install auratrace
```

Or better, use a virtual environment as shown above.

#### Version Conflicts

If you have version conflicts with existing packages:

```bash
# Create a fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
pip install auratrace
```

#### Memory Issues

If you encounter memory issues with large datasets:

```bash
# Install with memory optimization
pip install auratrace[performance]
```

### Getting Help

If you're still having issues:

1. Check the [GitHub Issues](https://github.com/auratrace/auratrace/issues)
2. Search for similar problems
3. Create a new issue with your error details

## 🔄 Updating AuraTrace

To update to the latest version:

```bash
pip install --upgrade auratrace
```

Or for a specific version:

```bash
pip install --upgrade auratrace==1.2.3
```

## 🗑️ Uninstalling

To uninstall AuraTrace:

```bash
pip uninstall auratrace
```

This will remove AuraTrace but keep your data and configuration files.

## 📚 Next Steps

After successful installation:

1. Read the [Quick Start Guide](quickstart.md) to get started
2. Check out [Basic Usage](basic-usage.md) for core concepts
3. Explore [Example Pipelines](examples/pipelines.md) for real-world usage

## 🔗 Related Documentation

- [Quick Start Guide](quickstart.md) - Get up and running quickly
- [Configuration Guide](configuration.md) - Configure AuraTrace settings
- [CLI Reference](cli-reference.md) - Command-line interface documentation
- [API Reference](api-reference.md) - Python API documentation 