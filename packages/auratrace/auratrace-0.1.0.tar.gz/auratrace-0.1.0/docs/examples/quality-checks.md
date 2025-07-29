# Data Quality Checks

This tutorial demonstrates data quality checking with [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## 1. Define Quality Rules

Create a YAML file (e.g., `quality_rules.yml`):

```yaml
rules:
  - name: null_check
    type: null_check
    parameters:
      max_null_percentage: 10.0
    severity: warning
```

## 2. Run Quality Check

```bash
auratrace check your_script.py --quality-rules quality_rules.yml
```

## 3. Interpret Results
- Warnings and errors are shown in the CLI and reports

## 4. More
- See [Quality Rules Guide](../quality-rules.md)
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 