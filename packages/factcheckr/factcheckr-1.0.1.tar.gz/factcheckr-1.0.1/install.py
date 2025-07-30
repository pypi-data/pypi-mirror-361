#!/usr/bin/env python3
"""
Cross-platform installation script for FactCheckr.
This script ensures the package works correctly on all platforms.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        if capture_output:
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"Error: Python 3.7+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_pip():
    """Check if pip is available and upgrade it."""
    try:
        result = run_command("pip --version")
        if result:
            print(f"✓ pip is available: {result.stdout.strip()}")
            
            # Upgrade pip
            print("Upgrading pip...")
            upgrade_result = run_command("python -m pip install --upgrade pip")
            if upgrade_result:
                print("✓ pip upgraded successfully")
            return True
    except Exception as e:
        print(f"Error checking pip: {e}")
        return False
    return False


def install_package_editable():
    """Install the package in editable mode."""
    print("Installing FactCheckr in editable mode...")
    result = run_command("pip install -e .")
    if result:
        print("✓ FactCheckr installed successfully in editable mode")
        return True
    return False


def install_package_from_pypi():
    """Install the package from PyPI."""
    print("Installing FactCheckr from PyPI...")
    result = run_command("pip install factcheckr")
    if result:
        print("✓ FactCheckr installed successfully from PyPI")
        return True
    return False


def test_installation():
    """Test if the installation works correctly."""
    print("Testing installation...")
    
    # Test module import
    try:
        import factcheckr
        print(f"✓ Module import successful (version: {factcheckr.__version__})")
    except ImportError as e:
        print(f"✗ Module import failed: {e}")
        return False
    
    # Test CLI as module
    result = run_command("python -m factcheckr --help")
    if result and result.returncode == 0:
        print("✓ CLI module execution works")
    else:
        print("✗ CLI module execution failed")
        return False
    
    # Test console script (may fail on some systems)
    result = run_command("factcheckr --help", check=False)
    if result and result.returncode == 0:
        print("✓ Console script works")
    else:
        print("⚠ Console script not available (use 'python -m factcheckr' instead)")
    
    # Test actual fact-checking
    result = run_command('python -m factcheckr "Test claim"')
    if result and result.returncode == 0:
        print("✓ Fact-checking functionality works")
        return True
    else:
        print("✗ Fact-checking functionality failed")
        return False


def get_platform_info():
    """Get platform information."""
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }
    
    print("Platform Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    return info


def check_scripts_directory():
    """Check if Python scripts directory is in PATH."""
    try:
        import site
        scripts_dir = None
        
        if platform.system() == "Windows":
            # Check various possible script locations on Windows
            possible_dirs = [
                os.path.join(sys.prefix, "Scripts"),
                os.path.join(site.getusersitepackages(), "..", "Scripts"),
                os.path.join(os.path.dirname(sys.executable), "Scripts"),
            ]
        else:
            # Unix-like systems
            possible_dirs = [
                os.path.join(sys.prefix, "bin"),
                os.path.join(site.getusersitepackages(), "..", "bin"),
                "/usr/local/bin",
                os.path.expanduser("~/.local/bin"),
            ]
        
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                scripts_dir = os.path.abspath(dir_path)
                if scripts_dir in path_dirs:
                    print(f"✓ Scripts directory in PATH: {scripts_dir}")
                    return True
                else:
                    print(f"⚠ Scripts directory not in PATH: {scripts_dir}")
        
        print("⚠ No suitable scripts directory found in PATH")
        print("  Use 'python -m factcheckr' instead of 'factcheckr'")
        return False
        
    except Exception as e:
        print(f"Error checking scripts directory: {e}")
        return False


def main():
    """Main installation function."""
    print("FactCheckr Installation Script")
    print("=" * 40)
    
    # Get platform info
    get_platform_info()
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    # Check scripts directory
    check_scripts_directory()
    print()
    
    # Determine installation method
    if os.path.exists("pyproject.toml") or os.path.exists("setup.py"):
        print("Local development installation detected")
        success = install_package_editable()
    else:
        print("Installing from PyPI")
        success = install_package_from_pypi()
    
    if not success:
        print("Installation failed!")
        sys.exit(1)
    
    print()
    
    # Test installation
    if test_installation():
        print("\n🎉 Installation completed successfully!")
        print("\nUsage:")
        print("  python -m factcheckr 'Your claim here'")
        print("  python -m factcheckr --interactive")
        print("  python -m factcheckr --help")
        
        # Check if console script works
        result = run_command("factcheckr --help", check=False)
        if result and result.returncode == 0:
            print("  factcheckr 'Your claim here'  # Console script also works")
    else:
        print("\n❌ Installation verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()