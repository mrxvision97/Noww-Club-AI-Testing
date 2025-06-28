#!/usr/bin/env python3
"""
Setup script for Noww Club AI local installation
Run this script to set up the environment and dependencies
"""

import os
import sys
import subprocess
import platform

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system dependencies based on OS"""
    system = platform.system().lower()
    
    if system == "linux":
        print("Installing Linux system dependencies...")
        commands = [
            ("sudo apt-get update", "Updating package lists"),
            ("sudo apt-get install -y portaudio19-dev python3-dev build-essential", "Installing audio and build dependencies")
        ]
    elif system == "darwin":  # macOS
        print("Installing macOS system dependencies...")
        commands = [
            ("brew install portaudio", "Installing PortAudio"),
        ]
    else:
        print("Windows detected. Please install dependencies manually:")
        print("- Install Microsoft Visual C++ Build Tools")
        print("- Install PortAudio from: http://www.portaudio.com/download.html")
        return True
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"Warning: {description} failed. Some features may not work.")
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Noww Club AI Environment Variables\n")
            f.write("# Get your API key from: https://platform.openai.com/api-keys\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✓ .env file created. Please add your OpenAI API key.")
    else:
        print("✓ .env file already exists")

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    # Core dependencies
    core_deps = [
        "streamlit>=1.46.0",
        "openai>=1.0.0",
        "langchain>=0.3.26",
        "langchain-openai>=0.3.25",
        "langchain-community>=0.3.0",
        "pandas>=2.3.0",
        "plotly>=6.1.2",
        "pydantic>=2.0.0",
        "duckduckgo-search>=5.0.0",
        "schedule>=1.2.0",
        "apscheduler>=3.10.0",
        "python-dotenv>=1.0.0"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}"):
            print(f"Failed to install {dep}")
            return False
    
    return True

def install_optional_dependencies():
    """Install optional dependencies with user confirmation"""
    
    # Vector database dependencies
    print("\nOptional: Enhanced Memory System (ChromaDB)")
    choice = input("Install ChromaDB for better conversation memory? (y/n): ").lower()
    if choice == 'y':
        vector_deps = ["chromadb>=0.4.0", "sentence-transformers>=2.2.0"]
        for dep in vector_deps:
            run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")
    
    # Voice dependencies
    print("\nOptional: Voice Input/Output")
    choice = input("Install voice capabilities? (y/n): ").lower()
    if choice == 'y':
        voice_deps = ["speechrecognition>=3.10.0", "pyttsx3>=2.90"]
        for dep in voice_deps:
            run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")
        
        # PyAudio requires special handling
        if not run_command("pip install pyaudio", "Installing PyAudio"):
            print("PyAudio installation failed. Voice input may not work.")

def main():
    """Main setup function"""
    print("=== Noww Club AI Local Setup ===\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Create necessary directories
    os.makedirs("user_profiles", exist_ok=True)
    os.makedirs("vector_db", exist_ok=True)
    
    # Setup steps
    steps = [
        ("Installing system dependencies", install_system_dependencies),
        ("Creating environment file", create_env_file),
        ("Installing Python dependencies", install_python_dependencies),
        ("Installing optional dependencies", install_optional_dependencies)
    ]
    
    for description, func in steps:
        print(f"\n--- {description} ---")
        if not func():
            print(f"Setup failed at: {description}")
            sys.exit(1)
    
    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Run: streamlit run app.py --server.port 5000")
    print("3. Open: http://localhost:5000")
    print("\nEnjoy chatting with your AI companion!")

if __name__ == "__main__":
    main()