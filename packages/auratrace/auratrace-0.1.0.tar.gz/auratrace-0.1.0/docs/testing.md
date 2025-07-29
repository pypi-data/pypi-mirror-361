# Testing Guide

This guide explains how to test [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## 1. Running Tests

```bash
pytest
```

## 2. Writing Tests
- Place tests in the `tests/` directory
- Use `pytest` for all new tests
- Mock external dependencies as needed

## 3. Test Coverage
- Check coverage with:
  ```bash
  pytest --cov=auratrace
  ```

## 4. Continuous Integration (CI)
- All PRs are tested via GitHub Actions
- See `.github/workflows/` for CI config

## 5. More
- For development setup, see [Development](development.md)
- For contributing, see [Contributing](contributing.md)
- Full source: [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git) 