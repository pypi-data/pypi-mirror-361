# Release Guide

This document explains how to create new releases of AUGR using the automated GitHub workflow.

## Setup (One-time)

### 1. PyPI API Token

Add your PyPI API token to GitHub repository secrets:

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Create a new API token with scope for this project
3. Copy the token (starts with `pypi-`)
4. Go to your GitHub repo → Settings → Secrets and variables → Actions
5. Click "New repository secret"
6. Name: `PYPI_API_TOKEN`
7. Value: Your PyPI token

### 2. GitHub Environment (Optional but Recommended)

For extra security, create a `release` environment:

1. Go to GitHub repo → Settings → Environments
2. Click "New environment"
3. Name: `release`
4. Add protection rules (e.g., require manual approval)

## Creating a Release

### Option 1: Automated Script (Recommended)

Use the bump version script:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/bump_version.py major
```

The script will:
- Update version in `pyproject.toml`
- Create git commit and tag
- Optionally push to trigger the release

### Option 2: Manual Process

1. **Update Version** - Edit `pyproject.toml`:

```toml
[project]
name = "augr"
version = "0.2.0"  # Update this
```

2. **Commit Changes**:

```bash
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main
```

3. **Create and Push Tag**:

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push tag to trigger workflow
git push origin v0.2.0
```

### 4. Monitor Workflow

1. Go to GitHub → Actions tab
2. Watch the "Release to PyPI" workflow run
3. It will:
   - Run tests on multiple Python versions
   - Build the package
   - Upload to PyPI
   - Create GitHub release with assets

## What Happens Automatically

1. **Tests**: Runs on Python 3.8-3.12
2. **Linting**: Black and Ruff checks
3. **Build**: Creates wheel and source distribution
4. **PyPI Upload**: Publishes to PyPI
5. **GitHub Release**: Creates release with notes and assets

## Manual Release (Fallback)

If the automated workflow fails:

```bash
# Build locally
uv run python -m build

# Upload manually
uv run twine upload dist/*
```

## Version Numbering

We use [Semantic Versioning](https://semver.org/):

- `v1.0.0` - Major release (breaking changes)
- `v0.2.0` - Minor release (new features)
- `v0.1.1` - Patch release (bug fixes)
- `v0.1.0-alpha.1` - Pre-release

## Release Checklist

Before creating a release:

- [ ] All tests pass locally
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if you have one)
- [ ] Version number is updated in `pyproject.toml`
- [ ] No uncommitted changes
- [ ] Ready to deploy to production

## Troubleshooting

### Workflow Fails

1. Check the Actions tab for error details
2. Common issues:
   - PyPI token expired
   - Version already exists on PyPI
   - Test failures
   - Build errors

### PyPI Upload Fails

1. Verify your `PYPI_API_TOKEN` secret is correct
2. Make sure the version number is unique
3. Check PyPI project permissions

### Creating Release Notes

You can customize the release notes by editing the workflow file or creating them manually on GitHub after the release is created.

## Advanced: Trusted Publishing

For even better security, consider setting up [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/):

1. Go to PyPI → Manage → Publishing
2. Add GitHub as trusted publisher
3. Update workflow to remove `password` parameter

This eliminates the need for API tokens. 