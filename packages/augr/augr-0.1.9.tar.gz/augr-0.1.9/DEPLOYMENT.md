# AUGR Deployment Guide

This guide covers different ways to deploy AUGR so users can install and use it with the `augr` command.

## Option 1: PyPI Package (Recommended for Public Distribution)

### 1. Prepare for PyPI

```bash
# Install build tools
uv pip install -e ".[dev]"

# Build the package
uv run python -m build

# Check the built package
ls dist/
# Should see: augr-0.1.0-py3-none-any.whl and augr-0.1.0.tar.gz
```

### 2. Upload to PyPI

```bash
# Upload to Test PyPI first (recommended)
uv run twine upload --repository testpypi dist/*

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ augr

# If everything works, upload to real PyPI
uv run twine upload dist/*
```

### 3. Users Install via PyPI

```bash
# Install globally
pip install augr

# Or with pipx for isolated installation
pipx install augr

# Or with uv
uv tool install augr

# Then use anywhere
augr
```

## Option 2: GitHub Direct Installation

### 1. Push to GitHub

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags
```

### 2. Users Install from GitHub

```bash
# Install latest from main branch
pip install git+https://github.com/yourusername/augr.git

# Install specific version/tag
pip install git+https://github.com/yourusername/augr.git@v0.1.0

# With uv
uv tool install git+https://github.com/yourusername/augr.git

# Then use
augr
```

## Option 3: Homebrew Formula (macOS/Linux)

### 1. Create Homebrew Formula

Create a file `Formula/augr.rb`:

```ruby
class Augr < Formula
  include Language::Python::Virtualenv

  desc "AI-powered dataset augmentation tool"
  homepage "https://github.com/yourusername/augr"
  url "https://github.com/yourusername/augr/archive/v0.1.0.tar.gz"
  sha256 "your-sha256-hash-here"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"augr", "--help"
  end
end
```

### 2. Users Install via Homebrew

```bash
# Add your tap
brew tap yourusername/augr

# Install
brew install augr

# Use
augr
```

## Option 4: Docker Container

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install -e .

# Set up entry point
ENTRYPOINT ["augr"]
```

### 2. Build and Push

```bash
# Build
docker build -t yourusername/augr:latest .

# Push to Docker Hub
docker push yourusername/augr:latest
```

### 3. Users Run with Docker

```bash
# Run interactively
docker run -it --rm \
  -v $(pwd):/workspace \
  -e BRAINTRUST_API_KEY=$BRAINTRUST_API_KEY \
  yourusername/augr:latest

# Create alias for convenience
echo 'alias augr="docker run -it --rm -v \$(pwd):/workspace -e BRAINTRUST_API_KEY=\$BRAINTRUST_API_KEY yourusername/augr:latest"' >> ~/.bashrc
```

## Option 5: Standalone Executable

### 1. Create with PyInstaller

```bash
# Install PyInstaller
uv pip install pyinstaller

# Create executable
pyinstaller --onefile --name augr run_augr.py

# Test
./dist/augr
```

### 2. Distribute Binary

Upload the binary from `dist/augr` to GitHub Releases or your distribution method.

## Option 6: Local Development Installation

For development or local team use:

```bash
# Clone repository
git clone https://github.com/yourusername/augr.git
cd augr

# Install in development mode
uv pip install -e .

# Or with regular pip
pip install -e .

# Use anywhere
augr
```

## Recommended Approach

For maximum reach and ease of use:

1. **Start with GitHub** (Option 2) for initial testing
2. **Move to PyPI** (Option 1) for stable releases
3. **Add Homebrew** (Option 3) for macOS users
4. **Provide Docker** (Option 4) for containerized environments

## Post-Installation User Experience

Once installed via any method, users can:

```bash
# Run the interactive CLI
augr

# Set up environment
export BRAINTRUST_API_KEY=your_key_here
# or create .env file in their project

# Use in any directory
cd my-project
augr
```

## Version Management

Update version in `pyproject.toml` and create git tags:

```bash
# Update version in pyproject.toml
# Then:
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags

# Rebuild and republish
uv run python -m build
uv run twine upload dist/*
``` 