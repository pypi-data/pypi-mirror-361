# Custom Rules Guide

You can extend [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) with your own quality and performance rules.

## 1. Custom Rule Structure

A custom rule is a Python function or class that implements a check on a dataframe.

```python
def my_custom_rule(df):
    # Your logic here
    if ...:
        return QualityIssue(...)
    return None
```

## 2. Registering Custom Rules

- Add your rule to the QualityEngine:
  ```python
  from auratrace.core.quality import QualityEngine
  engine = QualityEngine()
  engine.register_rule('my_rule', my_custom_rule)
  ```

## 3. Using Custom Rules
- Reference your rule in the YAML config or call it directly in code.

## 4. Example
```python
def check_negative_values(df):
    if (df < 0).any().any():
        return QualityIssue(rule_name='negative_check', description='Negative values found', severity='warning')
    return None
```

## 5. More
- See [Quality Rules](quality-rules.md)
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 