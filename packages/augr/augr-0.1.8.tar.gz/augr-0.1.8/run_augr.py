#!/usr/bin/env python3
"""
Simple entry point for the AUGR dataset augmentation tool
This file provides a fallback way to run AUGR without installing it as a package.
"""

import asyncio
import os
import sys


def main():
    """Main entry point that properly handles module imports"""
    try:
        # Add the current directory to Python path if running from source
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Import and run the CLI
        from augr.cli import main_async
        asyncio.run(main_async())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have all dependencies installed")
        print("   For development: uv pip install -e .")
        print("   For users: pip install augr")
        print("   Or use the installed command: augr")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 If this persists, please file an issue at: https://github.com/yourusername/augr/issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
