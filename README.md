# RAG Document Processor

A comprehensive toolkit to turn raw documents into RAG-ready chunks with metadata, overlap, and multiple export formats. Features a modern Gradio UI for easy document processing.

## Features

- **Multi-format Support**: PDF, DOCX, TXT, MD, Excel files
- **Smart Chunking**: Token-aware chunking with configurable overlap
- **Rich Metadata**: Automatic extraction and manual tagging
- **Multiple Export Formats**: JSONL, CSV, and direct vector database integration
- **Modern UI**: Gradio interface for easy document processing
- **Batch Processing**: Process entire folders of documents
- **Embedding Ready**: Optional sentence-transformers integration

## Quickstart

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
python setup.py
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install core dependencies
pip install -r requirements.txt

# Optional: Install advanced features
pip install -r requirements-optional.txt
```

**💡 If you encounter installation issues, see [MANUAL_SETUP.md](MANUAL_SETUP.md) for detailed troubleshooting.**

### 2. Launch the UI
```bash
python ui_gradio.py
```

### 3. Command Line Usage
```bash
# Process a single document
python rag_builder.py chunk content/intro-to-hse/01-overview.md --slug intro-hse-overview --section "Overview" --out out/intro-hse.overview.jsonl

# Batch process a folder
python rag_builder.py batch content/intro-to-hse --slug-prefix intro-hse --out out/intro-hse.jsonl

# Process with embeddings
python rag_builder.py chunk content/intro-to-hse/01-overview.md --embeddings --out out/intro-hse.overview.jsonl
```

## What You Get

### Token-aware chunking (default 280 tokens) with overlap (default 40 tokens)
- Sentence-respecting splits (no mid-sentence cuts)
- Configurable chunk sizes and overlap
- Smart handling of bullet points and lists

### Rich Metadata
- Title, slug, section, jurisdiction, version
- Effective dates, review dates, owner
- Tags, document type, source URL
- Automatic chunk indexing

### JSONL Export Format
```json
{
  "id": "intro-hse-overview:Overview:001",
  "text": "As an employer, you are responsible for managing health and safety...",
  "metadata": {
    "slug": "intro-hse-overview",
    "section": "Overview",
    "jurisdiction": "GB",
    "version": "1.0",
    "effective_date": "2025-09-01",
    "review_date": "2026-09-01",
    "owner": "DeanAI HSE",
    "tags": ["PDCA", "small-business"],
    "chunk_index": 1,
    "updated": "2025-09-02"
  },
  "embedding": [0.123, 0.456, ...]  // Optional
}
```

## Project Structure

```
Forge/
├── content/                 # Sample documents
│   └── intro-to-hse/
│       └── 01-overview.md
├── out/                     # Output directory (auto-created)
├── rag_builder.py          # Core processing logic
├── ui_gradio.py            # Gradio web interface
├── document_processor.py   # Multi-format document processing
├── embedding_utils.py      # Embedding generation utilities
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Design Principles

- **Single-topic documents**: Keep each source document focused on one topic
- **Flexible chunking**: Default 200-350 tokens, 10-20% overlap
- **Metadata-rich**: Comprehensive tagging for better retrieval
- **Format-agnostic**: Support for multiple document types
- **Vector-ready**: Optional embedding generation for immediate vector DB use

## Next Steps

1. **Vector Database Integration**: Connect to your preferred vector DB (pgvector, Qdrant, Weaviate, etc.)
2. **Custom Embeddings**: Use your own embedding models
3. **Advanced Metadata**: Add custom metadata extraction rules
4. **Batch Processing**: Scale to large document collections
5. **API Integration**: Expose as REST API for automation

## Contributing

Feel free to extend this project with:
- Additional document format support
- Custom metadata extractors
- Integration with specific vector databases
- Advanced chunking strategies
