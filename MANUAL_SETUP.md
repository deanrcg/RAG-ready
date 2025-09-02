# Manual Setup Guide

If you prefer to set up the project manually or encounter issues with the automated setup, follow these steps:

## Step 1: Check Python Version

Make sure you have Python 3.8 or higher installed:

```bash
python --version
# or
python3 --version
```

## Step 2: Create Virtual Environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install Core Dependencies

Install the basic dependencies first:

```bash
pip install --upgrade pip
pip install gradio==4.44.0 tiktoken==0.7.0 pyyaml==6.0.2 python-multipart==0.0.6
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

## Step 4: Test Basic Installation

Test that the core functionality works:

```bash
python test_system.py
```

## Step 5: Install Optional Dependencies (Optional)

If you want to use advanced features like PDF processing, DOCX support, or embeddings:

```bash
pip install -r requirements-optional.txt
```

Or install specific packages as needed:

```bash
# For PDF support
pip install pypdf2==3.0.1

# For Word documents
pip install python-docx==1.1.0

# For Excel files
pip install openpyxl==3.1.2 pandas==2.1.4

# For embeddings
pip install sentence-transformers==2.2.2 numpy==1.24.3

# For vector search
pip install faiss-cpu==1.7.4 chromadb==0.4.22
```

## Step 6: Create Output Directory

```bash
mkdir out
```

## Step 7: Test the System

```bash
python test_system.py
```

## Step 8: Launch the Application

### Web Interface
```bash
python ui_gradio.py
```

### Command Line
```bash
# Process a sample document
python rag_builder.py chunk content/intro-to-hse/01-overview.md --out out/test.jsonl
```

## Troubleshooting

### Common Issues

**1. Virtual Environment Not Activated**
- Make sure you see `(.venv)` at the start of your command prompt
- On Windows: `.venv\Scripts\activate`
- On Mac/Linux: `source .venv/bin/activate`

**2. Permission Errors**
- On Windows, try running PowerShell as Administrator
- On Mac/Linux, you might need to use `sudo` for some operations

**3. Package Installation Failures**
- Try upgrading pip first: `pip install --upgrade pip`
- Install packages one by one to identify problematic ones
- Check if you have sufficient disk space

**4. Import Errors**
- Make sure you're in the correct directory
- Ensure the virtual environment is activated
- Try reinstalling packages: `pip install --force-reinstall <package>`

**5. Memory Issues**
- Some packages like `sentence-transformers` require significant memory
- Try installing packages individually to identify memory-intensive ones

### Alternative Installation Methods

**Using Conda (if you prefer)**
```bash
conda create -n rag-processor python=3.9
conda activate rag-processor
pip install -r requirements.txt
```

**Using pip with --user flag**
```bash
pip install --user -r requirements.txt
```

**Minimal Installation (Basic Features Only)**
```bash
pip install gradio tiktoken pyyaml
```

## Verification

After setup, you should be able to:

1. ✅ Import core modules without errors
2. ✅ Run `python test_system.py` successfully
3. ✅ Launch the web interface with `python ui_gradio.py`
4. ✅ Process documents with `python rag_builder.py`

## Getting Help

If you continue to have issues:

1. Check the error messages carefully
2. Try the troubleshooting steps above
3. Install packages one by one to identify the problematic one
4. Check the project's README.md for more information
5. Ensure your Python version is compatible (3.8+)

## Next Steps

Once setup is complete:

1. **Start with the web interface**: `python ui_gradio.py`
2. **Try processing a sample document**: Use the provided sample files
3. **Explore the command line tools**: Check `python rag_builder.py --help`
4. **Read the documentation**: Check README.md and QUICKSTART.md
