# AUGR - AI Dataset Augmentation Tool

AI-powered dataset augmentation tool using Braintrust proxy with structured outputs.

## Features

- 🤖 **Structured AI Outputs**: Uses OpenAI's `beta.chat.completions.parse` with Pydantic schemas
- 🧠 **Braintrust Integration**: Works with Braintrust proxy for multiple AI providers
- 🔄 **Interactive Workflows**: Guided dataset augmentation with iterative refinement
- 📊 **Schema-aware Generation**: Automatically infers and respects dataset schemas
- ⚡ **Modern Tooling**: Built with `uv` for fast dependency management

## Installation

### Option 1: Install from PyPI

```bash
# Install globally
pip install augr

# Or with pipx (recommended for CLI tools)
pipx install augr

# Or with uv
uv tool install augr

# Then use anywhere
augr
```

### Option 2: Install from GitHub

```bash
# Install latest version
pip install git+https://github.com/Marviel/augr.git

# Or with uv
uv tool install git+https://github.com/Marviel/augr.git

# Then use anywhere
augr
```

### Option 3: Development Setup

For development or local installation:

```bash
git clone https://github.com/Marviel/augr.git
cd augr
uv sync --all-extras --dev

# Test the installation
uv run python test_installation.py

# Use anywhere
uv run augr
```

## Usage

### First Run Setup

The first time you run AUGR, it will guide you through setup:

```bash
augr
```

AUGR will:
1. Check for a Braintrust API key
2. If none found, guide you to get one from https://www.braintrust.dev/app/settings/api-keys
3. Save the key securely in `~/.augr/config.json`
4. Start the interactive tool

### Configuration

AUGR checks for your API key in this order:
1. `BRAINTRUST_API_KEY` environment variable
2. `~/.augr/config.json` file
3. Interactive setup (first time)

### Running

The tool provides an interactive CLI with two main modes:

1. **Guided Dataset Augmentation**: Interactive workflow with iterative refinement
2. **Direct JSON Upload**: Upload pre-generated samples directly

```bash
augr
```

### Uninstalling

To completely remove AUGR and all its configuration:

```bash
augr uninstall
# or
augr-uninstall
```

This will:
- Remove `~/.augr/` directory and all configuration
- Uninstall the AUGR package

### Development

Install with development dependencies:

```bash
uv pip install -e ".[dev]"
```

Run linting and formatting:

```bash
uv run black .
uv run ruff check .
```

## Architecture

- **`ai_client.py`**: Core AI interface with structured outputs
- **`augmentation_service.py`**: Main service for dataset augmentation
- **`cli.py`**: Interactive command-line interface
- **`models.py`**: Pydantic models for data structures
- **`braintrust_client.py`**: Braintrust API integration

## API Example

```python
from augr.ai_client import create_ai
from pydantic import BaseModel

class Response(BaseModel):
    message: str
    confidence: float

# Create AI client (reads BRAINTRUST_API_KEY from env)
ai = create_ai(model="gpt-4o", temperature=0.0)

# Generate structured output
result = await ai.gen_obj(
    schema=Response,
    messages=[{"role": "user", "content": "Hello!"}],
    thinking_enabled=True  # For reasoning models
)

print(result.message)  # Structured output
```

## Contributing

### Making a Release

This project uses automated releases via GitHub Actions:

1. Update version in `pyproject.toml`
2. Create and push a git tag: `git tag -a v0.2.0 -m "Release v0.2.0" && git push origin v0.2.0`
3. GitHub Actions will automatically:
   - Run tests
   - Build the package
   - Upload to PyPI
   - Create GitHub release

See [RELEASE.md](RELEASE.md) for detailed instructions.

### Development

```bash
# Clone and setup
git clone https://github.com/Marviel/augr.git
cd augr
uv sync --all-extras --dev

# Run tests
uv run python test_installation.py

# Format code
uv run black .
uv run ruff check --fix .

# Build package
uv run python -m build
```

## License

MIT
