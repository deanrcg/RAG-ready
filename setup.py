#!/usr/bin/env python3
"""
Setup script for RAG Document Processor
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if capture_output and e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create a virtual environment."""
    if os.path.exists(".venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv .venv", "Creating virtual environment")

def install_dependencies():
    """Install project dependencies."""
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
        activate_cmd = ".venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        pip_cmd = ".venv/bin/pip"
        activate_cmd = "source .venv/bin/activate"
    
    # First, try to upgrade pip
    print("🔄 Upgrading pip...")
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip", capture_output=False)
    
    # Install core dependencies
    success = run_command(f"{pip_cmd} install -r requirements.txt", "Installing core dependencies")
    
    if success:
        print("✅ Core dependencies installed successfully")
        print("💡 To install optional dependencies (PDF, DOCX, embeddings support), run:")
        print(f"   {pip_cmd} install -r requirements-optional.txt")
    else:
        print("⚠️  Some dependencies failed to install. You can still use basic features.")
        print("💡 Try installing manually:")
        print(f"   {pip_cmd} install gradio tiktoken pyyaml")
    
    return success

def create_output_directory():
    """Create output directory."""
    output_dir = Path("out")
    if not output_dir.exists():
        output_dir.mkdir()
        print("✅ Created output directory")
    else:
        print("✅ Output directory already exists")
    return True

def test_installation():
    """Test if the installation works."""
    print("🧪 Testing installation...")
    
    # Test imports
    try:
        import gradio
        print("✅ Gradio imported successfully")
    except ImportError:
        print("❌ Gradio import failed")
        return False
    
    try:
        import tiktoken
        print("✅ Tiktoken imported successfully")
    except ImportError:
        print("❌ Tiktoken import failed")
        return False
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError:
        print("❌ PyYAML import failed")
        return False
    
    # Test document processor (optional)
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        print("✅ Document processor imported successfully")
    except ImportError as e:
        print(f"⚠️  Document processor import failed (optional): {e}")
    
    # Test embedding utils (optional)
    try:
        from embedding_utils import EmbeddingGenerator
        print("✅ Embedding utilities imported successfully")
    except ImportError as e:
        print(f"⚠️  Embedding utilities import failed (optional): {e}")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up RAG Document Processor...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        print("💡 Try running manually: python -m venv .venv")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create output directory
    if not create_output_directory():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("⚠️  Some optional components failed to import")
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source .venv/bin/activate")
    
    print("2. Launch the web interface:")
    print("   python ui_gradio.py")
    
    print("3. Or use the command line:")
    print("   python rag_builder.py chunk content/intro-to-hse/01-overview.md --out out/test.jsonl")
    
    print("\n💡 Optional features:")
    print("   - Install PDF/DOCX support: pip install -r requirements-optional.txt")
    print("   - Test the system: python test_system.py")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
