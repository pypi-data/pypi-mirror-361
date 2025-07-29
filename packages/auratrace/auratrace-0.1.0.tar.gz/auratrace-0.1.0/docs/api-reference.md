# API Reference

This API reference covers the main Python interfaces for [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## Main Modules

### `auratrace.ai`
- `AIAssistant`: The main AI-powered assistant class.
- `LLMProvider` and subclasses: Abstractions for pluggable LLMs (OpenAI, Hugging Face, custom, local, user-supplied).

#### Example: Using the AI Assistant
```python
from auratrace.ai import AIAssistant
ai = AIAssistant(provider="huggingface", model="mistralai/Mistral-7B-Instruct-v0.2")
result = ai.analyze_lineage(lineage_data, "What operations were performed?")
print(result.response)
```

### `auratrace.core`
- `Tracer`: Captures data lineage and pipeline operations.
- `LineageEngine`: Builds and visualizes lineage graphs.
- `QualityEngine`: Runs data quality checks.
- `Profiler`: Profiles dataframes and operations.
- `PerformanceEngine`: Monitors and analyzes performance.

#### Example: Tracing a Pipeline
```python
from auratrace.core.tracer import Tracer
tracer = Tracer()
with tracer.trace_session():
    # Your pandas code here
    ...
```

### `auratrace.cli`
- CLI entrypoints for all commands (see [CLI Reference](cli-reference.md)).

## Data Structures
- `AIAnalysis`: Result object for AI queries.
- `QualityIssue`: Represents a data quality issue.
- `LineageGraph`: Data structure for lineage DAGs.

## More
- For full source code, see [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).
- For advanced usage, see [Architecture](architecture.md) and [AI Assistant](ai-assistant.md). 