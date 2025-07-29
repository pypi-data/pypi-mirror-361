# Performance Tuning Guide

This guide helps you optimize pipelines with [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## 1. Profiling Pipelines

AuraTrace automatically profiles execution time and memory usage for each operation.

- Use `auratrace run` to trace your script.
- View performance summaries with `auratrace view`.

## 2. Detecting Bottlenecks

- The performance engine highlights slow operations and memory spikes.
- Use the AI assistant for optimization suggestions:
  ```bash
  auratrace ask session.json "How can I optimize my pipeline?"
  ```

## 3. Best Practices
- Minimize unnecessary dataframe copies
- Use vectorized operations
- Profile with real data
- Set quality rules for performance thresholds

## 4. Memory Optimization
- Monitor memory deltas in reports
- Use Dask for large datasets
- Clean up unused dataframes

## 5. More
- For advanced tuning, see [Architecture](architecture.md)
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 