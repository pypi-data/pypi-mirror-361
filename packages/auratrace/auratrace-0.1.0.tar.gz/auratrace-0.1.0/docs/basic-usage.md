# Basic Usage Guide

This guide covers the core usage patterns of [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) for data scientists and engineers.

## 1. Tracing a Pipeline

AuraTrace works transparently with your pandas, Dask, or PyArrow code. Simply run your script with AuraTrace:

```bash
auratrace run your_script.py
```

## 2. Viewing Data Lineage

After running a pipeline, view the lineage and results:

```bash
auratrace view session.json
```

This displays a DAG of operations and dataframes, showing how your data was transformed.

## 3. Checking Data Quality

Run quality checks using a YAML rules file:

```bash
auratrace check session.json --quality-rules examples/quality_rules.yml
```

## 4. Using the AI Assistant

Ask natural language questions about your pipeline:

```bash
auratrace ask session.json "What operations were performed?"
```

If you haven't configured an LLM, AuraTrace will prompt you to set up a provider (OpenAI, Hugging Face, etc.).

## 5. Example: Simple Pipeline

```python
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df_filtered = df[df['A'] > 1]
df_grouped = df.groupby('A').sum()
```

Run and analyze:

```bash
auratrace run examples/simple_pipeline.py
```

## 6. More Resources

- [Installation Guide](installation.md)
- [CLI Reference](cli-reference.md)
- [API Reference](api-reference.md)
- [GitHub Repository](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 