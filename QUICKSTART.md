# Quick Start Guide

Get up and running with the RAG Document Processor in minutes!

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
# Run the setup script (recommended)
python setup.py

# Or manually:
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Test the Installation
```bash
python test_system.py
```

### 3. Launch the Web Interface
```bash
python ui_gradio.py
```

Open your browser to `http://localhost:7860`

## 📝 Your First Document

### Option 1: Web Interface (Easiest)
1. Go to the "Text Input" tab
2. Paste your document text
3. Fill in metadata (title, tags, etc.)
4. Click "Process Text"
5. Copy the JSONL output

### Option 2: Command Line
```bash
# Process a single file
python rag_builder.py chunk content/intro-to-hse/01-overview.md --out out/my_document.jsonl

# Process with embeddings
python rag_builder.py chunk content/intro-to-hse/01-overview.md --embeddings --out out/my_document.jsonl

# Batch process a folder
python rag_builder.py batch content/sample-documents --out out/batch_output.jsonl
```

## 📄 Supported File Types

- **Markdown (.md)** - With front-matter metadata
- **Text (.txt)** - Plain text documents
- **PDF (.pdf)** - PDF documents
- **Word (.docx)** - Microsoft Word documents
- **Excel (.xlsx, .xls)** - Spreadsheets

## ⚙️ Key Features

### Smart Chunking
- **Token-aware**: Respects token boundaries
- **Sentence-respecting**: No mid-sentence cuts
- **Configurable**: 150-500 tokens per chunk
- **Overlap**: 0-120 token overlap between chunks

### Rich Metadata
- Document title, slug, section
- Jurisdiction, document type, version
- Effective dates, review dates
- Owner, source URL, tags
- Automatic chunk indexing

### Multiple Output Formats
- **JSONL**: Standard format for vector databases
- **CSV**: Easy to view in spreadsheets
- **With embeddings**: Ready for similarity search

## 🎯 Common Use Cases

### 1. Process a Single Document
```bash
python rag_builder.py chunk my_document.pdf --out chunks.jsonl
```

### 2. Process with Custom Metadata
```bash
python rag_builder.py chunk my_document.md \
  --title "My Document" \
  --slug my-doc \
  --section "Main" \
  --tags "important,urgent" \
  --out chunks.jsonl
```

### 3. Generate Embeddings
```bash
python rag_builder.py chunk my_document.txt \
  --embeddings \
  --embedding-model "all-MiniLM-L6-v2" \
  --out chunks_with_embeddings.jsonl
```

### 4. Batch Process Multiple Files
```bash
python rag_builder.py batch my_documents_folder \
  --slug-prefix "my-docs" \
  --embeddings \
  --out all_chunks.jsonl
```

## 🔧 Configuration

### Chunking Settings
- **Default chunk size**: 280 tokens
- **Default overlap**: 40 tokens
- **Range**: 150-500 tokens (chunk), 0-120 tokens (overlap)

### Embedding Models
- **Fast**: `all-MiniLM-L6-v2` (384 dimensions)
- **Balanced**: `all-mpnet-base-v2` (768 dimensions)
- **High Quality**: `all-MiniLM-L12-v2` (384 dimensions)

## 📊 Output Format

### JSONL Format
```json
{
  "id": "document-slug:section:001",
  "text": "Chunk content here...",
  "metadata": {
    "title": "Document Title",
    "slug": "document-slug",
    "section": "Main",
    "jurisdiction": "GB",
    "version": "1.0",
    "tags": ["tag1", "tag2"],
    "chunk_index": 1,
    "updated": "2025-01-01"
  },
  "embedding": [0.123, 0.456, ...]  // Optional
}
```

## 🔗 Next Steps

### 1. Vector Database Integration
```python
# Example with ChromaDB
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
collection = client.create_collection("my_docs")

# Add chunks with embeddings
collection.add(
    documents=[chunk["text"] for chunk in chunks],
    embeddings=[chunk["embedding"] for chunk in chunks],
    metadatas=[chunk["metadata"] for chunk in chunks]
)
```

### 2. Similarity Search
```python
# Search for similar documents
results = collection.query(
    query_texts=["safety guidelines"],
    n_results=5
)
```

### 3. RAG Pipeline Integration
- Use chunks as context for LLM responses
- Implement semantic search
- Build question-answering systems

## 🆘 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Memory Issues with Large Documents**
```bash
# Use smaller chunk sizes
python rag_builder.py chunk large_doc.pdf --chunk-size 200 --out chunks.jsonl
```

**Slow Embedding Generation**
```bash
# Use faster model
python rag_builder.py chunk doc.pdf --embedding-model "all-MiniLM-L6-v2" --out chunks.jsonl
```

### Getting Help
- Check the full README.md for detailed documentation
- Run `python test_system.py` to diagnose issues
- Review error messages in the console output

## 🎉 You're Ready!

Your RAG Document Processor is now set up and ready to transform documents into searchable chunks. Start processing your documents and building powerful RAG applications!
