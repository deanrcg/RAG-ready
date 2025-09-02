#!/usr/bin/env python3
"""
Gradio UI for RAG Document Processor
"""

import gradio as gr
import tempfile
import os
import json
from pathlib import Path

# Import our modules with fallbacks
try:
    from document_processor import DocumentProcessor, clean_text
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    print("⚠️  Document processor not available - limited file support")

try:
    from rag_builder import parse_front_matter, build_items
    RAG_BUILDER_AVAILABLE = True
except ImportError:
    RAG_BUILDER_AVAILABLE = False
    print("⚠️  RAG builder not available")

try:
    from embedding_utils import EmbeddingGenerator, MODEL_CONFIGS
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("⚠️  Embedding utilities not available")

def process_text(text, section, slug, title, jurisdiction, doc_type, version, eff_date, rev_date, owner, tags, chunk_size, overlap, generate_embeddings, embedding_model):
    """Process text input and return JSONL chunks."""
    if not text.strip():
        return "Please enter some text.", 0
    
    try:
        # Parse front matter if present
        if text.startswith('---'):
            fm, body = parse_front_matter(text)
        else:
            fm, body = {}, text
        
        # Set up metadata
        fm_default = {
            "title": title or "Untitled Document",
            "slug": slug or "untitled",
            "jurisdiction": jurisdiction or "GB",
            "doc_type": doc_type or "guidance",
            "version": version or "1.0",
            "effective_date": eff_date or "",
            "review_date": rev_date or "",
            "owner": owner or "Document Owner",
            "source_url": "",
            "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
        }
        
        base_meta = {**fm_default, **fm}
        section = section or fm.get("section", "Main")
        
        # Build chunks
        items = build_items(body, base_meta, section, chunk_size, overlap,
                           generate_embeddings, embedding_model)
        
        # Convert to JSONL
        jsonl = "\n".join(json.dumps(it, ensure_ascii=False) for it in items)
        return jsonl, len(items)
    
    except Exception as e:
        return f"Error processing text: {str(e)}", 0

def process_file(file, section, slug, title, jurisdiction, doc_type, version, eff_date, rev_date, owner, tags, chunk_size, overlap, generate_embeddings, embedding_model):
    """Process uploaded file and return JSONL chunks."""
    if file is None:
        return "Please upload a file.", 0
    
    try:
        if DOCUMENT_PROCESSOR_AVAILABLE:
            processor = DocumentProcessor()
            if processor.can_process(file.name):
                text, file_metadata = processor.extract_text(file.name)
                text = clean_text(text)
            else:
                with open(file.name, 'r', encoding='utf-8') as f:
                    text = f.read()
                file_metadata = {}
        else:
            with open(file.name, 'r', encoding='utf-8') as f:
                text = f.read()
            file_metadata = {}
        
        if file.name.lower().endswith('.md'):
            fm, body = parse_front_matter(text)
        else:
            fm, body = {}, text
        
        fm_default = {
            "title": title or file_metadata.get("title", os.path.basename(file.name)),
            "slug": slug or os.path.splitext(os.path.basename(file.name))[0],
            "jurisdiction": jurisdiction or "GB",
            "doc_type": doc_type or "guidance",
            "version": version or "1.0",
            "effective_date": eff_date or "",
            "review_date": rev_date or "",
            "owner": owner or "HSE-App",
            "source_url": "",
            "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
            "source_format": file_metadata.get("format", "unknown"),
        }
        
        base_meta = {**fm_default, **fm}
        section = section or fm.get("section","Main")
        
        items = build_items(body, base_meta, section, chunk_size, overlap,
                           generate_embeddings, embedding_model)
        
        jsonl = "\n".join(json.dumps(it, ensure_ascii=False) for it in items)
        return jsonl, len(items)
    
    except Exception as e:
        return f"Error processing file: {str(e)}", 0

def get_embedding_models():
    """Get available embedding models."""
    if EMBEDDING_AVAILABLE:
        return list(MODEL_CONFIGS.keys())
    return ["fast"]  # Default fallback

def create_demo():
    """Create the Gradio demo interface."""
    
    # Get embedding models
    embedding_models = get_embedding_models()
    
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📄 RAG Document Processor")
        gr.Markdown("Transform your documents into RAG-ready chunks with rich metadata.")
        
        with gr.Tabs():
            # Text Input Tab
            with gr.Tab("📝 Text Input"):
                with gr.Row():
                    with gr.Column(scale=2):
                        text_input = gr.Textbox(
                            label="Document Text",
                            placeholder="Paste your document text here...",
                            lines=10
                        )
                    with gr.Column(scale=1):
                        with gr.Group():
                            gr.Markdown("### Metadata")
                            section = gr.Textbox(label="Section", value="Main")
                            slug = gr.Textbox(label="Slug", placeholder="document-slug")
                            title = gr.Textbox(label="Title", placeholder="Document Title")
                            jurisdiction = gr.Dropdown(
                                choices=["GB", "US", "EU", "AU", "CA"],
                                value="GB",
                                label="Jurisdiction"
                            )
                            doc_type = gr.Dropdown(
                                choices=["guidance", "policy", "procedure", "manual", "report"],
                                value="guidance",
                                label="Document Type"
                            )
                            version = gr.Textbox(label="Version", value="1.0")
                            eff_date = gr.Textbox(label="Effective Date", placeholder="YYYY-MM-DD")
                            rev_date = gr.Textbox(label="Review Date", placeholder="YYYY-MM-DD")
                            owner = gr.Textbox(label="Owner", value="Document Owner")
                            tags = gr.Textbox(label="Tags", placeholder="tag1,tag2,tag3")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        chunk_size = gr.Slider(
                            minimum=150, maximum=500, value=280, step=10,
                            label="Chunk Size (tokens)"
                        )
                        overlap = gr.Slider(
                            minimum=0, maximum=120, value=40, step=10,
                            label="Overlap (tokens)"
                        )
                    with gr.Column(scale=1):
                        generate_embeddings = gr.Checkbox(
                            label="Generate Embeddings",
                            value=False
                        )
                        embedding_model = gr.Dropdown(
                            choices=embedding_models,
                            value=embedding_models[0],
                            label="Embedding Model"
                        )
                
                process_btn = gr.Button("🔄 Process Text", variant="primary")
                
                with gr.Row():
                    output_text = gr.Textbox(
                        label="JSONL Output",
                        lines=10,
                        placeholder="Processed chunks will appear here..."
                    )
                    chunk_count = gr.Number(label="Chunks Generated", value=0)
                
                process_btn.click(
                    fn=process_text,
                    inputs=[
                        text_input, section, slug, title, jurisdiction, doc_type,
                        version, eff_date, rev_date, owner, tags, chunk_size, overlap,
                        generate_embeddings, embedding_model
                    ],
                    outputs=[output_text, chunk_count]
                )
            
            # File Upload Tab
            with gr.Tab("📁 File Upload"):
                with gr.Row():
                    with gr.Column(scale=2):
                        file_input = gr.File(
                            label="Upload Document",
                            file_types=[".txt", ".md", ".pdf", ".docx", ".xlsx"],
                            file_count="single"
                        )
                    with gr.Column(scale=1):
                        with gr.Group():
                            gr.Markdown("### Metadata")
                            file_section = gr.Textbox(label="Section", value="Main")
                            file_slug = gr.Textbox(label="Slug", placeholder="document-slug")
                            file_title = gr.Textbox(label="Title", placeholder="Document Title")
                            file_jurisdiction = gr.Dropdown(
                                choices=["GB", "US", "EU", "AU", "CA"],
                                value="GB",
                                label="Jurisdiction"
                            )
                            file_doc_type = gr.Dropdown(
                                choices=["guidance", "policy", "procedure", "manual", "report"],
                                value="guidance",
                                label="Document Type"
                            )
                            file_version = gr.Textbox(label="Version", value="1.0")
                            file_eff_date = gr.Textbox(label="Effective Date", placeholder="YYYY-MM-DD")
                            file_rev_date = gr.Textbox(label="Review Date", placeholder="YYYY-MM-DD")
                            file_owner = gr.Textbox(label="Owner", value="Document Owner")
                            file_tags = gr.Textbox(label="Tags", placeholder="tag1,tag2,tag3")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        file_chunk_size = gr.Slider(
                            minimum=150, maximum=500, value=280, step=10,
                            label="Chunk Size (tokens)"
                        )
                        file_overlap = gr.Slider(
                            minimum=0, maximum=120, value=40, step=10,
                            label="Overlap (tokens)"
                        )
                    with gr.Column(scale=1):
                        file_generate_embeddings = gr.Checkbox(
                            label="Generate Embeddings",
                            value=False
                        )
                        file_embedding_model = gr.Dropdown(
                            choices=embedding_models,
                            value=embedding_models[0],
                            label="Embedding Model"
                        )
                
                file_process_btn = gr.Button("🔄 Process File", variant="primary")
                
                with gr.Row():
                    file_output_text = gr.Textbox(
                        label="JSONL Output",
                        lines=10,
                        placeholder="Processed chunks will appear here..."
                    )
                    file_chunk_count = gr.Number(label="Chunks Generated", value=0)
                
                file_process_btn.click(
                    fn=process_file,
                    inputs=[
                        file_input, file_section, file_slug, file_title, file_jurisdiction,
                        file_doc_type, file_version, file_eff_date, file_rev_date,
                        file_owner, file_tags, file_chunk_size, file_overlap,
                        file_generate_embeddings, file_embedding_model
                    ],
                    outputs=[file_output_text, file_chunk_count]
                )
            
            # Batch Processing Tab
            with gr.Tab("📦 Batch Processing"):
                gr.Markdown("### Batch Processing")
                gr.Markdown("Upload multiple files for batch processing.")
                
                batch_files = gr.File(
                    label="Upload Multiple Files",
                    file_types=[".txt", ".md", ".pdf", ".docx", ".xlsx"],
                    file_count="multiple"
                )
                
                batch_process_btn = gr.Button("🔄 Process Batch", variant="primary")
                batch_output = gr.Textbox(
                    label="Batch Results",
                    lines=10,
                    placeholder="Batch processing results will appear here..."
                )
                
                batch_process_btn.click(
                    fn=lambda x: "Batch processing coming soon!",
                    inputs=[batch_files],
                    outputs=[batch_output]
                )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("""
        ### 📚 How to Use
        
        1. **Text Input**: Paste your document text and configure metadata
        2. **File Upload**: Upload a document file (TXT, MD, PDF, DOCX, XLSX)
        3. **Batch Processing**: Upload multiple files for batch processing
        
        ### 📊 Output Format
        
        The system generates JSONL files with rich metadata, ready for vector database integration.
        
        ### 🔧 Advanced Features
        
        - **Embeddings**: Generate vector embeddings for similarity search
        - **Custom Metadata**: Add tags, dates, ownership, and more
        - **Configurable Chunking**: Adjust chunk size and overlap
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="127.0.0.1",  # Use localhost instead of 0.0.0.0
        server_port=7860,
        share=False,
        show_error=True
    )
