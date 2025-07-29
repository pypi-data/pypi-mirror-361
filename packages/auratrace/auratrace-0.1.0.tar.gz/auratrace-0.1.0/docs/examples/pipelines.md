# Example Pipelines

This tutorial shows how to trace and analyze real-world pipelines with [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## 1. Example Pipeline

```python
import pandas as pd

df = pd.read_csv('data.csv')
df = df[df['value'] > 0]
df['log_value'] = np.log(df['value'])
df_grouped = df.groupby('category').agg({'log_value': 'mean'})
```

## 2. Tracing the Pipeline

```bash
auratrace run your_pipeline.py --output results.json
```

## 3. Viewing Results

```bash
auratrace view results.json
```

## 4. More
- For more examples, see [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 