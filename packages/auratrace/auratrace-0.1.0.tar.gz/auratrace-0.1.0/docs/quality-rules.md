# Quality Rules Guide

AuraTrace supports flexible data quality rules to help you maintain high data standards.

## 1. Rule Format (YAML)

Rules are defined in a YAML file. Example:

```yaml
rules:
  - name: null_check
    description: Check for excessive null values
    type: null_check
    parameters:
      max_null_percentage: 50.0
    severity: warning
  - name: uniqueness_check
    description: Check for duplicate values
    type: uniqueness_check
    column: id
    severity: error
```

## 2. Built-in Rule Types
- `null_check`: Detects columns with too many nulls
- `uniqueness_check`: Checks for duplicate values
- `range_check`: Ensures values fall within a range
- `type_check`: Validates data types
- `custom`: User-defined Python logic

## 3. Using Rules

- In CLI:
  ```bash
  auratrace check script.py --quality-rules rules.yml
  ```
- In code:
  ```python
  from auratrace.core.quality import QualityEngine
  engine = QualityEngine()
  engine.load_rules_from_yaml('rules.yml')
  issues = engine.check_dataframe(df)
  ```

## 4. Best Practices
- Use descriptive names and descriptions
- Set appropriate severity levels
- Combine multiple rules for robust checks

## 5. More
- See [examples/quality_rules.yml](../examples/quality_rules.yml)
- For advanced rules, see [Custom Rules](custom-rules.md)
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 