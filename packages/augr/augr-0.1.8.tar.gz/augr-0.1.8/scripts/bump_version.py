#!/usr/bin/env python3
"""
Utility script to bump version and create releases
"""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("❌ Version not found in pyproject.toml")
        sys.exit(1)

    return match.group(1)

def bump_version(current_version, bump_type):
    """Bump version number"""
    parts = current_version.split('.')
    if len(parts) != 3:
        print("❌ Version must be in format x.y.z")
        sys.exit(1)

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print("❌ Bump type must be major, minor, or patch")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"

def update_pyproject_version(new_version):
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # More specific regex to only match the project version in the [project] section
    new_content = re.sub(
        r'(\[project\].*?)version = "[^"]+"',
        rf'\1version = "{new_version}"',
        content,
        flags=re.DOTALL
    )

    pyproject_path.write_text(new_content)
    print(f"✅ Updated pyproject.toml to version {new_version}")

def run_command(cmd, check=True):
    """Run shell command"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0 and check:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(1)

    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [major|minor|patch]")
        print("\nExample:")
        print("  python scripts/bump_version.py patch    # 0.1.0 -> 0.1.1")
        print("  python scripts/bump_version.py minor    # 0.1.0 -> 0.2.0")
        print("  python scripts/bump_version.py major    # 0.1.0 -> 1.0.0")
        sys.exit(1)

    bump_type = sys.argv[1]

    # Get current version
    current_version = get_current_version()
    print(f"📦 Current version: {current_version}")

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"🆕 New version: {new_version}")

    # Confirm with user
    response = input(f"\n🤔 Bump version from {current_version} to {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)

    # Update pyproject.toml
    update_pyproject_version(new_version)

    # Git operations
    print("\n📝 Creating git commit and tag...")

    # Add and commit
    run_command("git add pyproject.toml")
    run_command(f'git commit -m "Bump version to {new_version}"')

    # Create tag
    run_command(f'git tag -a v{new_version} -m "Release version {new_version}"')

    print(f"\n🎉 Version bumped to {new_version}!")
    print("\nNext steps:")
    print("1. Review the changes: git show")
    print(f"2. Push to trigger release: git push origin main && git push origin v{new_version}")
    print("3. Monitor GitHub Actions for automatic PyPI deployment")

    # Ask if user wants to push immediately
    response = input("\n🚀 Push now to trigger release? (y/N): ")
    if response.lower() == 'y':
        print("\n📤 Pushing to GitHub...")
        run_command("git push origin main")
        run_command(f"git push origin v{new_version}")
        print(f"\n🎉 Release v{new_version} triggered!")
        print("Check GitHub Actions for deployment status.")

if __name__ == "__main__":
    main()
