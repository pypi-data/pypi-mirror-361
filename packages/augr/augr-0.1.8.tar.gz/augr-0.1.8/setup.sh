#!/bin/bash

echo "🚀 Setting up AUGR Dataset Augmentation Tool"
echo "==========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed"
    echo "💡 Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Found uv"

# Create virtual environment with uv
echo "📦 Creating virtual environment with uv..."
uv venv

# Install dependencies from pyproject.toml
echo "📥 Installing dependencies from pyproject.toml..."
uv pip install -e .

# Install dev dependencies (optional)
read -p "🔧 Install development dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Installing development dependencies..."
    uv pip install -e ".[dev]"
fi

# Copy environment file
echo "📋 Setting up environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from env.example"
    echo "⚠️  Please edit .env and add your BRAINTRUST_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your BRAINTRUST_API_KEY"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Run the tool: python run_augr.py"
echo ""
echo "Alternative ways to run:"
echo "  uv run python run_augr.py        # Run with uv (auto-manages venv)"
echo "  uv run python -m augr.cli        # Run CLI module directly"  
echo "  uv run augr                      # Use installed script entry point" 