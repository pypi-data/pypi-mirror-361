# AuraTrace 🔍

[![PyPI version](https://badge.fury.io/py/auratrace.svg)](https://badge.fury.io/py/auratrace)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/auratrace/auratrace/workflows/Tests/badge.svg)](https://github.com/auratrace/auratrace/actions)
[![Documentation](https://readthedocs.org/projects/auratrace/badge/?version=latest)](https://auratrace.readthedocs.io/)

**AI-powered data lineage and observability tool for Python** that transparently traces data pipelines using pandas, Dask, and PyArrow, capturing lineage, profiling data, detecting quality issues, and providing AI-assisted root cause analysis and visualization.

## ✨ Features

### 🔍 **Automatic Data Lineage**
- Transparent tracing of pandas operations
- Captures dataframe metadata and relationships
- Builds comprehensive DAG of data transformations
- Supports Dask and PyArrow for large-scale processing

### 📊 **Data Profiling & Quality**
- Automatic data profiling and statistics
- PII detection and privacy compliance
- Custom quality rules with YAML configuration
- Real-time quality issue detection and reporting

### ⚡ **Performance Monitoring**
- Execution time tracking for each operation
- Memory usage monitoring and optimization
- Bottleneck identification and suggestions
- Performance regression detection

### 🤖 **AI-Powered Analysis**
- Natural language queries about your data
- AI-assisted root cause analysis
- Performance optimization suggestions
- Automated data quality insights

### 📈 **Visualization & Reporting**
- Interactive lineage graphs
- Performance dashboards
- Quality issue reports
- Pipeline comparison tools

### 🛠️ **Developer-Friendly**
- Simple CLI interface
- Python API for custom integrations
- Comprehensive logging and debugging
- Extensible plugin architecture

## 🚀 Quick Start

### Installation

```bash
pip install auratrace
```

### Basic Usage

```python
# Your existing pandas code works unchanged!
import pandas as pd

# AuraTrace automatically traces these operations
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df_filtered = df[df['A'] > 1]
df_grouped = df.groupby('A').sum()

print("Pipeline completed!")
```

Run with AuraTrace:

```bash
auratrace run your_script.py
```

### CLI Commands

```bash
# Run a pipeline with tracing
auratrace run pipeline.py

# View pipeline results
auratrace view session.json

# Ask AI questions about your data
auratrace ask session.json "What operations were performed?"

# Check data quality
auratrace check session.json

# Compare pipeline versions
auratrace compare session1.json session2.json

# Initialize project configuration
auratrace init
```

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Complete setup instructions
- **[Quick Start](docs/quickstart.md)** - Get up and running in 5 minutes
- **[CLI Reference](docs/cli-reference.md)** - Complete command documentation
- **[API Reference](docs/api-reference.md)** - Python API documentation
- **[Examples](docs/examples/)** - Real-world usage examples

## 🏗️ Architecture

AuraTrace consists of several core components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tracer        │    │   Profiler      │    │   Lineage       │
│                 │    │                 │    │                 │
│ • Pandas hooks  │    │ • Data stats    │    │ • DAG building  │
│ • Operation     │    │ • PII detection │    │ • Graph export  │
│   capture       │    │ • Schema        │    │ • Visualization │
│ • Performance   │    │   analysis      │    │ • Impact        │
│   monitoring    │    │ • Quality       │    │   analysis      │
└─────────────────┘    │   checks        │    └─────────────────┘
                       └─────────────────┘
                                │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Quality       │    │   Performance   │    │   AI Assistant  │
│   Engine        │    │   Engine        │    │                 │
│                 │    │                 │    │                 │
│ • Rule engine   │    │ • Metrics       │    │ • OpenAI        │
│ • YAML config   │    │   collection    │    │   integration   │
│ • Issue         │    │ • Bottleneck    │    │ • Natural       │
│   detection     │    │   detection     │    │   language      │
│ • Custom rules  │    │ • Optimization  │    │   queries       │
└─────────────────┘    │   suggestions   │    └─────────────────┘
                       └─────────────────┘
```

## 🔧 Installation Options

### Basic Installation
```bash
pip install auratrace
```

### Full Installation (with AI features)
```bash
pip install auratrace[all]
```

### Development Installation
```bash
git clone https://github.com/auratrace/auratrace.git
cd auratrace
pip install -e .
```

## 🎯 Use Cases

### Data Science Teams
- **Pipeline Debugging**: Quickly identify where data issues originate
- **Performance Optimization**: Find bottlenecks in data processing
- **Quality Assurance**: Ensure data meets quality standards
- **Documentation**: Automatically generate pipeline documentation

### Data Engineering
- **Lineage Tracking**: Understand data dependencies and impact
- **Quality Monitoring**: Set up automated quality checks
- **Performance Tuning**: Optimize large-scale data processing
- **Compliance**: Track PII and sensitive data handling

### Machine Learning
- **Feature Engineering**: Trace feature transformations
- **Model Validation**: Ensure data quality for model training
- **Experiment Tracking**: Compare different data preprocessing approaches
- **Reproducibility**: Maintain complete data lineage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/auratrace/auratrace.git
cd auratrace
pip install -e ".[dev]"
pytest
```

### Ways to Contribute

- 🐛 **Report bugs** - Use [GitHub Issues](https://github.com/auratrace/auratrace/issues)
- 💡 **Suggest features** - Start a [Discussion](https://github.com/auratrace/auratrace/discussions)
- 📝 **Improve docs** - Submit PRs to enhance documentation
- 🔧 **Fix bugs** - Pick up issues labeled "good first issue"
- 🚀 **Add features** - Implement new functionality

## 📊 Project Status

- ✅ **Core tracing engine** - Complete
- ✅ **Data profiling** - Complete
- ✅ **Quality engine** - Complete
- ✅ **Performance monitoring** - Complete
- ✅ **CLI interface** - Complete
- ✅ **AI assistant** - Complete
- ✅ **Documentation** - Complete
- ✅ **Tests** - Complete
- 🔄 **Visualization** - In progress
- 🔄 **Dask integration** - In progress

## 📈 Roadmap

### v1.0 (Current)
- ✅ Core tracing and profiling
- ✅ Quality checks and AI analysis
- ✅ CLI and basic visualization

### v1.1 (Next)
- 🔄 Enhanced visualization
- 🔄 Dask and PyArrow support
- 🔄 Plugin architecture

### v1.2 (Future)
- 🔄 Real-time monitoring
- 🔄 Web dashboard
- 🔄 Enterprise features

## 🆘 Support

### Getting Help

- 📚 **[Documentation](docs/)** - Comprehensive guides and examples
- 💬 **[Discussions](https://github.com/auratrace/auratrace/discussions)** - Ask questions and share ideas
- 🐛 **[Issues](https://github.com/auratrace/auratrace/issues)** - Report bugs and request features
- 📧 **Email** - [support@auratrace.io](mailto:support@auratrace.io)

### Community

- 🌐 **[Website](https://auratrace.io)** - Project homepage
- 📖 **[Blog](https://auratrace.io/blog)** - Latest updates and tutorials
- 🐦 **[Twitter](https://twitter.com/auratrace)** - Follow for updates
- 💼 **[LinkedIn](https://linkedin.com/company/auratrace)** - Professional updates

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pandas** - For the excellent data manipulation library
- **OpenAI** - For AI capabilities
- **NetworkX** - For graph operations
- **Rich** - For beautiful terminal output
- **Typer** - For CLI framework

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=auratrace/auratrace&type=Date)](https://star-history.com/#auratrace/auratrace&Date)

---

**Made with ❤️ by the AuraTrace team**

*Empowering data scientists and engineers with transparent, AI-powered observability.* 

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