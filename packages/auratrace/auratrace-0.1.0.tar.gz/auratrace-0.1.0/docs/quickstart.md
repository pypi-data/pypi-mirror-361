# Quick Start Guide

Get up and running with AuraTrace in 5 minutes! This guide will walk you through the basics of using AuraTrace to trace and analyze your data pipelines.

## 🚀 Step 1: Installation

First, install AuraTrace:

```bash
pip install auratrace
```

## 📝 Step 2: Create Your First Pipeline

Create a simple Python script to test AuraTrace:

```python
# simple_pipeline.py
import pandas as pd
import numpy as np

# Load some sample data
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45],
    'score': [85, 90, 75, 88, 92]
})

# Perform some operations
df_filtered = df[df['age'] > 30]
df_grouped = df.groupby('age').agg({'score': 'mean'}).reset_index()

print("Pipeline completed successfully!")
print(f"Original data: {len(df)} rows")
print(f"Filtered data: {len(df_filtered)} rows")
print(f"Grouped data: {len(df_grouped)} rows")
```

## 🔍 Step 3: Run with AuraTrace

Run your script with AuraTrace to automatically trace the pipeline:

```bash
auratrace run simple_pipeline.py
```

You'll see output like this:

```
🔍 AuraTrace: Starting pipeline execution
📊 Dataframe created: df (5 rows, 4 columns)
🔧 Operation: filter (age > 30) - 2 rows affected
📊 Dataframe created: df_filtered (2 rows, 4 columns)
🔧 Operation: groupby (age) - 3 rows affected
📊 Dataframe created: df_grouped (3 rows, 2 columns)
✅ Pipeline completed successfully!
📈 Performance Summary:
   - Total operations: 3
   - Total execution time: 0.15s
   - Memory usage: 2.1 MB
```

## 📊 Step 4: View the Results

View detailed information about your pipeline:

```bash
# View the session data
auratrace view auratrace_session_*.json

# Or use the latest session
auratrace view --latest
```

This will show you:
- All dataframes created
- Operations performed
- Performance metrics
- Data quality information

## 🤖 Step 5: Ask Questions (AI Features)

If you have an OpenAI API key set up, you can ask questions about your data:

```bash
# Set your API key
export OPENAI_API_KEY=your_api_key_here

# Ask questions about your pipeline
auratrace ask auratrace_session_*.json "What operations were performed?"
auratrace ask auratrace_session_*.json "How much data was filtered out?"
auratrace ask auratrace_session_*.json "What are the performance bottlenecks?"
```

## 🔍 Step 6: Check Data Quality

AuraTrace automatically checks data quality. View quality issues:

```bash
auratrace check auratrace_session_*.json
```

## 📈 Step 7: Compare Pipelines

Run your pipeline with different parameters and compare:

```python
# pipeline_v2.py
import pandas as pd

# Same data but different filtering
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45],
    'score': [85, 90, 75, 88, 92]
})

# Different filter condition
df_filtered = df[df['score'] > 85]  # Changed from age > 30
df_grouped = df.groupby('name').agg({'age': 'mean'}).reset_index()  # Changed grouping

print("Pipeline v2 completed!")
```

Run both versions and compare:

```bash
auratrace run simple_pipeline.py
auratrace run pipeline_v2.py
auratrace compare auratrace_session_*.json
```

## 🎯 Key Features You Just Used

### 1. **Automatic Tracing**
- AuraTrace automatically detects pandas operations
- Captures dataframe metadata and lineage
- Tracks performance metrics

### 2. **Performance Monitoring**
- Execution time for each operation
- Memory usage tracking
- Bottleneck identification

### 3. **Data Quality Checks**
- Automatic null value detection
- Data type validation
- Custom quality rules support

### 4. **AI-Powered Analysis**
- Natural language queries about your data
- Performance optimization suggestions
- Root cause analysis

### 5. **Pipeline Comparison**
- Compare different pipeline versions
- Identify changes in data flow
- Performance regression detection

## 🔧 Configuration

Create a configuration file for custom settings:

```bash
auratrace init
```

This creates:
- `auratrace_config.yaml` - Main configuration
- `quality_rules.yaml` - Data quality rules
- `example_pipeline.py` - Example script

## 📚 Next Steps

Now that you've got the basics, explore:

1. **[Basic Usage](basic-usage.md)** - Learn core concepts
2. **[CLI Reference](cli-reference.md)** - Complete command reference
3. **[Quality Rules](quality-rules.md)** - Set up custom quality checks
4. **[AI Assistant](ai-assistant.md)** - Advanced AI features
5. **[Example Pipelines](examples/pipelines.md)** - Real-world examples

## 🆘 Need Help?

- **Documentation**: Check the guides above
- **GitHub Issues**: [Report bugs or request features](https://github.com/auratrace/auratrace/issues)
- **Discussions**: [Ask questions](https://github.com/auratrace/auratrace/discussions)

## 🎉 Congratulations!

You've successfully:
- ✅ Installed AuraTrace
- ✅ Traced your first data pipeline
- ✅ Viewed pipeline results
- ✅ Used AI-powered analysis
- ✅ Checked data quality
- ✅ Compared pipeline versions

You're now ready to use AuraTrace for your data science projects! 