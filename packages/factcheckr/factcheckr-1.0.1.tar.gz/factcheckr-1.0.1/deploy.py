#!/usr/bin/env python3
"""
Deployment script for FactCheckr package.
Handles building, testing, and publishing to PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import re


def run_command(cmd, check=True, capture_output=True, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        if capture_output:
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
        return None


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("Checking prerequisites...")
    
    required_packages = ['build', 'twine', 'pytest']
    missing_packages = []
    
    for package in required_packages:
        result = run_command(f"python -c 'import {package}'")
        if result and result.returncode == 0:
            print(f"✓ {package} is available")
        else:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        result = run_command(install_cmd)
        if result:
            print("✓ Missing packages installed")
        else:
            print("✗ Failed to install missing packages")
            return False
    
    return True


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'src/factcheckr.egg-info', '*.egg-info']
    
    for dir_pattern in dirs_to_clean:
        if '*' in dir_pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(dir_pattern):
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"✓ Removed {path}")
        else:
            if os.path.exists(dir_pattern):
                shutil.rmtree(dir_pattern)
                print(f"✓ Removed {dir_pattern}")
    
    print("✓ Build artifacts cleaned")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    # Check if tests directory exists
    if not os.path.exists('tests'):
        print("⚠ No tests directory found, skipping tests")
        return True
    
    # Run pytest
    result = run_command("python -m pytest tests/ -v")
    if result and result.returncode == 0:
        print("✓ All tests passed")
        return True
    else:
        print("✗ Tests failed")
        return False


def validate_package_structure():
    """Validate the package structure."""
    print("Validating package structure...")
    
    required_files = [
        'pyproject.toml',
        'README.md',
        'LICENSE',
        'src/factcheckr/__init__.py',
        'src/factcheckr/core.py',
        'src/factcheckr/cli.py',
        'src/factcheckr/__main__.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"✗ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✓ Package structure is valid")
    return True


def check_version_consistency():
    """Check version consistency across files."""
    print("Checking version consistency...")
    
    # Read version from pyproject.toml
    pyproject_version = None
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']*)["\'']', content)
            if match:
                pyproject_version = match.group(1)
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return False
    
    # Read version from __init__.py
    init_version = None
    try:
        with open('src/factcheckr/__init__.py', 'r') as f:
            content = f.read()
            match = re.search(r'__version__\s*=\s*["\']([^"\']*)["\'']', content)
            if match:
                init_version = match.group(1)
    except Exception as e:
        print(f"Error reading __init__.py: {e}")
        return False
    
    if pyproject_version and init_version:
        if pyproject_version == init_version:
            print(f"✓ Version consistency: {pyproject_version}")
            return True
        else:
            print(f"✗ Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}")
            return False
    else:
        print("✗ Could not find version in one or both files")
        return False


def build_package():
    """Build the package."""
    print("Building package...")
    
    result = run_command("python -m build")
    if result and result.returncode == 0:
        print("✓ Package built successfully")
        
        # List built files
        if os.path.exists('dist'):
            dist_files = os.listdir('dist')
            print("Built files:")
            for file in dist_files:
                print(f"  - {file}")
        
        return True
    else:
        print("✗ Package build failed")
        return False


def check_package():
    """Check the built package with twine."""
    print("Checking package with twine...")
    
    result = run_command("twine check dist/*")
    if result and result.returncode == 0:
        print("✓ Package check passed")
        return True
    else:
        print("✗ Package check failed")
        return False


def test_installation():
    """Test installation of the built package."""
    print("Testing package installation...")
    
    # Create a temporary virtual environment for testing
    import tempfile
    import venv
    
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = os.path.join(temp_dir, 'test_env')
        
        # Create virtual environment
        print("Creating test virtual environment...")
        venv.create(venv_dir, with_pip=True)
        
        # Determine the correct python executable path
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
            pip_exe = os.path.join(venv_dir, 'Scripts', 'pip.exe')
        else:  # Unix-like
            python_exe = os.path.join(venv_dir, 'bin', 'python')
            pip_exe = os.path.join(venv_dir, 'bin', 'pip')
        
        # Install the package
        dist_files = [f for f in os.listdir('dist') if f.endswith('.whl')]
        if not dist_files:
            print("✗ No wheel file found in dist/")
            return False
        
        wheel_file = os.path.join('dist', dist_files[0])
        install_cmd = f'"{pip_exe}" install "{wheel_file}"'
        
        result = run_command(install_cmd)
        if not result or result.returncode != 0:
            print("✗ Failed to install package in test environment")
            return False
        
        # Test the installation
        test_cmd = f'"{python_exe}" -m factcheckr "Test installation claim"'
        result = run_command(test_cmd)
        if result and result.returncode == 0:
            print("✓ Package installation test passed")
            return True
        else:
            print("✗ Package installation test failed")
            return False


def publish_to_pypi(test_pypi=False):
    """Publish the package to PyPI."""
    repository = "testpypi" if test_pypi else "pypi"
    print(f"Publishing to {'Test ' if test_pypi else ''}PyPI...")
    
    # Check for API token
    token_env = "TEST_PYPI_API_TOKEN" if test_pypi else "PYPI_API_TOKEN"
    if not os.environ.get(token_env):
        print(f"⚠ {token_env} environment variable not set")
        print("Please set your PyPI API token or use interactive authentication")
    
    # Upload command
    if test_pypi:
        upload_cmd = "twine upload --repository testpypi dist/*"
    else:
        upload_cmd = "twine upload dist/*"
    
    result = run_command(upload_cmd, capture_output=False)
    if result and result.returncode == 0:
        print(f"✓ Successfully published to {'Test ' if test_pypi else ''}PyPI")
        return True
    else:
        print(f"✗ Failed to publish to {'Test ' if test_pypi else ''}PyPI")
        return False


def main():
    """Main deployment function."""
    print("FactCheckr Deployment Script")
    print("=" * 40)
    
    # Parse command line arguments
    test_pypi = '--test' in sys.argv
    skip_tests = '--skip-tests' in sys.argv
    skip_upload = '--skip-upload' in sys.argv
    
    if test_pypi:
        print("🧪 Test PyPI mode enabled")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Step 2: Validate package structure
    if not validate_package_structure():
        sys.exit(1)
    
    # Step 3: Check version consistency
    if not check_version_consistency():
        sys.exit(1)
    
    # Step 4: Run tests
    if not skip_tests and not run_tests():
        print("❌ Tests failed. Use --skip-tests to bypass.")
        sys.exit(1)
    
    # Step 5: Clean build artifacts
    clean_build_artifacts()
    
    # Step 6: Build package
    if not build_package():
        sys.exit(1)
    
    # Step 7: Check package
    if not check_package():
        sys.exit(1)
    
    # Step 8: Test installation
    if not test_installation():
        print("⚠ Installation test failed, but continuing...")
    
    # Step 9: Publish to PyPI
    if not skip_upload:
        if publish_to_pypi(test_pypi):
            print("\n🎉 Deployment completed successfully!")
            if test_pypi:
                print("Package published to Test PyPI")
                print("Test installation: pip install -i https://test.pypi.org/simple/ factcheckr")
            else:
                print("Package published to PyPI")
                print("Install with: pip install factcheckr")
        else:
            sys.exit(1)
    else:
        print("\n✓ Build completed successfully (upload skipped)")
        print("To upload manually:")
        if test_pypi:
            print("  twine upload --repository testpypi dist/*")
        else:
            print("  twine upload dist/*")


if __name__ == "__main__":
    main()