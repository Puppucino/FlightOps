"""
Helper script to install dependencies
"""
import subprocess
import sys
import os

def main():
    print("Installing dependencies...")
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version}")
    print()
    
    # Get the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found!")
        sys.exit(1)
    
    print(f"Installing from: {requirements_file}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            cwd=backend_dir,
            check=True,
            capture_output=False
        )
        print()
        print("✓ Dependencies installed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print(f"✗ Error installing dependencies: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
