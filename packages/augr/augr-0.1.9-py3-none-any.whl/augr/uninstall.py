"""
Uninstall utility for AUGR with multi-project configuration support.
"""

import subprocess
import sys
from pathlib import Path

from .config import cleanup_all_configs


def main():
    """Main uninstall function for AUGR"""
    print("🗑️  AUGR Uninstaller")
    print("=" * 30)
    print()
    
    # Confirm uninstall
    print("This will:")
    print("• Remove all AUGR projects and configurations (~/.augr/)")
    print("• Uninstall the augr package")
    print()
    
    try:
        confirm = input("Are you sure you want to uninstall AUGR? [y/N]: ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("❌ Uninstall cancelled")
            return
        
        success = True
        
        # Remove configuration files
        print("\n🗂️  Removing configuration files...")
        try:
            if cleanup_all_configs():
                print("✅ Configuration files removed")
            else:
                print("ℹ️  No configuration files found")
        except Exception as e:
            print(f"⚠️  Could not remove config files: {e}")
            success = False
        
        # Uninstall package
        print("\n📦 Uninstalling augr package...")
        try:
            # Try to get the installed package path for verification
            try:
                import augr
                package_path = Path(augr.__file__).parent.parent
                print(f"Found package at: {package_path}")
            except Exception:
                pass
            
            # Run pip uninstall
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "augr", "-y"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Package uninstalled successfully")
            else:
                print(f"⚠️  Package uninstall had issues: {result.stderr}")
                success = False
                
        except Exception as e:
            print(f"❌ Failed to uninstall package: {e}")
            success = False
        
        # Final message
        print("\n" + "=" * 30)
        if success:
            print("✅ AUGR has been completely removed from your system")
            print("Thank you for using AUGR!")
        else:
            print("⚠️  Uninstall completed with some issues")
            print("You may need to manually remove remaining files")
        
    except KeyboardInterrupt:
        print("\n❌ Uninstall cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during uninstall: {e}")


if __name__ == "__main__":
    main() 