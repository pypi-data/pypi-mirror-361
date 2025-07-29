# Architecture Overview

This document describes the architecture of [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## System Diagram

```
+-------------------+     +-------------------+     +-------------------+
|     Tracer        | --> |    Profiler       | --> |    Lineage        |
| (Hooks, Capture)  |     | (Stats, PII)     |     | (DAG, Graph)      |
+-------------------+     +-------------------+     +-------------------+
         |                        |                        |
         v                        v                        v
+-------------------+     +-------------------+     +-------------------+
|   Quality Engine  |     | Performance Eng.  |     |   AI Assistant    |
| (Rules, Checks)   |     | (Timing, Memory)  |     | (LLM, Analysis)   |
+-------------------+     +-------------------+     +-------------------+
```

## Components

- **Tracer**: Hooks into pandas/Dask/PyArrow to capture all operations and dataframes.
- **Profiler**: Profiles data, detects PII, and gathers statistics.
- **Lineage Engine**: Builds a DAG of all data transformations and relationships.
- **Quality Engine**: Applies quality rules and detects issues.
- **Performance Engine**: Monitors execution time and memory usage.
- **AI Assistant**: Provides natural language analysis and root cause suggestions using pluggable LLMs.

## Design Principles
- **Transparency**: No code changes needed for tracing.
- **Extensibility**: Plugin architecture for new rules, engines, and LLMs.
- **Performance**: Minimal overhead, scalable to large pipelines.
- **Open Source**: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git)

## More
- For developer details, see [Development](development.md).
- For contributing, see [Contributing](contributing.md). 