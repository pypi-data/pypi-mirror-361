# Configuration Guide

This guide explains how to configure [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) for your project.

## 1. Configuration File

AuraTrace supports a YAML config file (default: `.auratrace.yml`). Example:

```yaml
default_quality_rules: quality.yml
output_directory: ./auratrace_reports
enable_ai: true
ai_model: mistralai/Mistral-7B-Instruct-v0.2
```

## 2. Environment Variables

- `AURATRACE_LLM_PROVIDER`: LLM provider (openai, huggingface, custom, local, user)
- `AURATRACE_LLM_MODEL`: Model name or path
- `AURATRACE_LLM_API_KEY`: API key for provider

## 3. CLI Options

All config options can be overridden via CLI flags (see [CLI Reference](cli-reference.md)).

## 4. .env File

You can use a `.env` file to set environment variables for local development.

## 5. In-Code Configuration

You can also configure AuraTrace directly in Python:

```python
from auratrace.ai import AIAssistant
ai = AIAssistant(provider="huggingface", model="mistralai/Mistral-7B-Instruct-v0.2")
```

## 6. Quality Rules

Quality rules are configured in a YAML file (see [Quality Rules](quality-rules.md)).

## 7. More
- For all options, see [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git). 