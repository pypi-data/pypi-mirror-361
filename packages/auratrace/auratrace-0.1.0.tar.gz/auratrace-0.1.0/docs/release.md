# Release Process

This guide describes the release and deployment process for [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## 1. Versioning
- Follows [Semantic Versioning](https://semver.org/)
- Update `pyproject.toml` and `CHANGELOG.md` for each release

## 2. Changelog
- Document all changes in `CHANGELOG.md`

## 3. Publishing to PyPI
```bash
python -m build
python -m twine upload dist/*
```

## 4. GitHub Releases
- Tag the release in Git
- Create a release on [GitHub](https://github.com/Cosmos-Coder-Ray/AuraTrace.git/releases)

## 5. More
- For contributing, see [Contributing](contributing.md)
- For development, see [Development](development.md) 