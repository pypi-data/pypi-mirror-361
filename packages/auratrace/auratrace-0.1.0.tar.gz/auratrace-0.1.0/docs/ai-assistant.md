# AI Assistant Guide

The AI assistant in [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) provides natural language analysis, root cause suggestions, and optimization tips using pluggable LLMs.

## 1. Supported Providers
- OpenAI (GPT-3.5, GPT-4)
- Hugging Face (API/local)
- Custom API endpoints
- Local models (transformers)
- User-supplied Python functions

## 2. Configuration
- Set provider/model/API key via environment, CLI, or code (see [Configuration](configuration.md)).

## 3. Usage
- CLI:
  ```bash
  auratrace ask session.json "What operations were performed?" --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.2
  ```
- Python:
  ```python
  from auratrace.ai import AIAssistant
  ai = AIAssistant(provider="openai", api_key="sk-...", model="gpt-4")
  result = ai.analyze_lineage(lineage_data, "Explain the pipeline")
  print(result.response)
  ```

## 4. Advanced Features
- Change provider/model at runtime
- Upload your own LLM or function
- Use any API key (OpenAI, Claude, Gemini, etc.)
- Model download and dependency install are optional

## 5. Troubleshooting
- If the AI assistant is not ready, AuraTrace will prompt for setup
- See [CLI Reference](cli-reference.md) for all options

## 6. More
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 