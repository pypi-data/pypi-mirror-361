#!/usr/bin/env python3
"""
PyPI Publishing Script for Restorant
Automates the build and upload process to PyPI
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def get_current_version():
    """Get current version from pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        content = f.read()
        match = re.search(r'version = "([^"]+)"', content)
        if match:
            return match.group(1)
    return None

def update_version(new_version):
    """Update version in pyproject.toml and setup.py"""
    # Update pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    
    with open("pyproject.toml", "w") as f:
        f.write(content)
    
    # Update setup.py if it exists
    if os.path.exists("setup.py"):
        with open("setup.py", "r") as f:
            content = f.read()
        
        content = re.sub(r'version="[^"]+"', f'version="{new_version}"', content)
        
        with open("setup.py", "w") as f:
            f.write(content)
    
    print(f"Updated version to {new_version}")

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    run_command("rmdir /s /q dist", check=False)
    run_command("rmdir /s /q build", check=False)
    run_command("rmdir /s /q *.egg-info", check=False)

def build_package():
    """Build the package"""
    print("Building package...")
    run_command("python -m build")

def check_package():
    """Check the built package"""
    print("Checking package...")
    run_command("twine check dist/*")

def upload_to_testpypi():
    """Upload to TestPyPI"""
    print("Uploading to TestPyPI...")
    run_command("twine upload --repository testpypi dist/*")

def upload_to_pypi():
    """Upload to PyPI"""
    print("Uploading to PyPI...")
    run_command("twine upload dist/*")

def main():
    """Main publishing process"""
    print("🍽️ Restorant PyPI Publishing Script")
    print("=" * 50)
    
    # Check if .pypirc is configured
    if not os.path.exists(".pypirc"):
        print("❌ .pypirc file not found!")
        print("Please create .pypirc with your PyPI credentials")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Ask for new version
    print("\nVersion options:")
    print("1. Patch (1.0.0 -> 1.0.1)")
    print("2. Minor (1.0.0 -> 1.1.0)")
    print("3. Major (1.0.0 -> 2.0.0)")
    print("4. Custom version")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if current_version is None:
        print("❌ Could not determine current version!")
        sys.exit(1)
        
    if choice == "1":
        # Patch version
        parts = current_version.split(".")
        new_version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
    elif choice == "2":
        # Minor version
        parts = current_version.split(".")
        new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
    elif choice == "3":
        # Major version
        parts = current_version.split(".")
        new_version = f"{int(parts[0]) + 1}.0.0"
    elif choice == "4":
        # Custom version
        new_version = input("Enter new version (e.g., 1.0.1): ").strip()
    else:
        print("Invalid choice!")
        sys.exit(1)
    
    print(f"\nNew version will be: {new_version}")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != "y":
        print("Cancelled!")
        sys.exit(0)
    
    # Update version
    update_version(new_version)
    
    # Clean previous builds
    clean_build()
    
    # Build package
    build_package()
    
    # Check package
    check_package()
    
    # Ask where to upload
    print("\nUpload options:")
    print("1. TestPyPI (for testing)")
    print("2. PyPI (production)")
    print("3. Both")
    
    upload_choice = input("Enter choice (1-3): ").strip()
    
    if upload_choice == "1":
        upload_to_testpypi()
    elif upload_choice == "2":
        upload_to_pypi()
    elif upload_choice == "3":
        upload_to_testpypi()
        upload_to_pypi()
    else:
        print("Invalid choice!")
        sys.exit(1)
    
    print(f"\n✅ Successfully published Restorant v{new_version}!")
    print(f"Install with: pip install restorant=={new_version}")

if __name__ == "__main__":
    main() 