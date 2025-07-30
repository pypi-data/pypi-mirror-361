# PyPI Publishing Setup Guide

This guide explains how to set up automated publishing for the Erdo Agents SDK to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. **GitHub Repository**: The SDK should be in its own repository (`erdoai/erdo-agents-sdk`)

## 1. PyPI Account Setup

### Create PyPI Accounts
1. **PyPI (Production)**: https://pypi.org/account/register/
2. **TestPyPI (Testing)**: https://test.pypi.org/account/register/

### Register Package Name
1. Go to https://pypi.org/manage/account/
2. Reserve the package name `erdo-agents-sdk` (if available)

## 2. GitHub Repository Setup

### Trusted Publishing (Recommended)
Modern PyPI supports trusted publishing without API tokens:

1. **On PyPI**:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - PyPI project name: `erdo-agents-sdk`
     - Owner: `erdoai`
     - Repository name: `erdo-agents-sdk`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`

2. **On TestPyPI**:
   - Go to https://test.pypi.org/manage/account/publishing/
   - Add the same configuration with environment name: `testpypi`

### GitHub Environments
1. Go to your repository Settings > Environments
2. Create two environments:
   - **`pypi`**: For production releases
   - **`testpypi`**: For testing releases

## 3. Release Process

### Version Management
The package uses **automatic versioning** from Git tags:
- Tags like `v1.0.0` → Package version `1.0.0`
- Development commits → Version like `1.0.0+dev.5.g1234567`

### Automatic Release (Recommended)

1. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **The GitHub Action will automatically**:
   - Run tests across Python 3.9-3.13
   - Build source and wheel distributions
   - Publish to PyPI

### Manual Testing Release

To test on TestPyPI before production:

1. **Use workflow dispatch**:
   - Go to Actions tab in GitHub
   - Select "Publish to PyPI" workflow
   - Click "Run workflow" on main branch
   - This publishes to TestPyPI only

2. **Test the TestPyPI package**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ erdo-agents-sdk
   ```

## 4. Package Installation

After successful release:

```bash
# Install the package
pip install erdo-agents-sdk

# Install with optional dependencies
pip install erdo-agents-sdk[all]
pip install erdo-agents-sdk[data,web]

# Verify installation
python -c "import erdo; print(erdo.__version__)"
```

## 5. Development Workflow

### Local Development
```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check erdo/
black --check erdo/
isort --check-only erdo/
mypy erdo/

# Build package locally
python -m build
```

### Pre-release Checklist
- [ ] All tests pass locally
- [ ] Version bump is appropriate (major.minor.patch)
- [ ] CHANGELOG.md is updated (if you have one)
- [ ] Documentation is up to date

## 6. Troubleshooting

### Common Issues

1. **Package name already exists**:
   - Choose a different name in `pyproject.toml`
   - Update GitHub environments accordingly

2. **Trusted publishing fails**:
   - Verify environment names match exactly
   - Check repository and workflow names are correct
   - Ensure the workflow runs from the main branch

3. **Build fails**:
   - Check Python version compatibility
   - Ensure all dependencies are properly declared
   - Verify package structure is correct

4. **Import errors after installation**:
   - Check `__init__.py` exports are correct
   - Verify package structure matches `pyproject.toml`

### Debug Commands

```bash
# Test package build locally
python -m build

# Check package contents
tar -tzf dist/erdo-agents-sdk-*.tar.gz
unzip -l dist/erdo_agents_sdk-*.whl

# Test local installation
pip install dist/*.whl
python -c "import erdo; print('Success')"

# Check package metadata
pip show erdo-agents-sdk
```

## 7. Configuration Files

The publishing process uses these configuration files:

- `.github/workflows/publish.yml` - Main publishing workflow
- `.github/workflows/ci.yml` - CI testing workflow
- `pyproject.toml` - Package configuration and metadata

## 8. Security Considerations

- **Never commit API tokens** to the repository
- Use **trusted publishing** instead of API tokens when possible
- **Protect the main branch** to prevent accidental releases
- **Review changes carefully** before tagging releases

## 9. Repository Split Checklist

When moving to a separate repository:

- [ ] Create `erdoai/erdo-agents-sdk` repository
- [ ] Copy `erdo-agents-sdk/` contents to the new repo root
- [ ] Set up PyPI trusted publishing for the new repository
- [ ] Create GitHub environments (`pypi`, `testpypi`)
- [ ] Test the publishing workflow with a pre-release
- [ ] Update documentation and import instructions
