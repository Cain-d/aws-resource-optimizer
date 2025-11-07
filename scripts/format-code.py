#!/usr/bin/env python3
"""
Simple code formatter for the project.
Run this before committing to ensure consistent formatting.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"⚠️ {description} completed with warnings")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Format code and run basic checks."""
    project_root = Path(__file__).parent.parent
    
    print("🔧 Formatting AWS Resource Optimizer code...")
    print(f"Project root: {project_root}")
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    # Install formatting tools if needed
    print("Installing formatting tools...")
    subprocess.run([sys.executable, "-m", "pip", "install", "black", "isort"], 
                  capture_output=True)
    
    # Format Python code
    success = True
    success &= run_command("python -m black src/ tests/ --line-length 88", "Black formatting")
    success &= run_command("python -m isort src/ tests/ --profile black", "Import sorting")
    
    # Run basic tests
    success &= run_command("python -m pytest tests/ -v", "Basic tests")
    
    if success:
        print("\n🎉 All formatting and tests completed successfully!")
        print("Your code is ready to commit and push to GitHub.")
    else:
        print("\n⚠️ Some issues were found, but they've been fixed where possible.")
        print("Please review the output above and commit your changes.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())