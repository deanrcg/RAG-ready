#!/usr/bin/env python3
import re, os, json, argparse, sys
from datetime import date
from typing import List, Dict, Tuple

# Import our new modules
try:
    from document_processor import DocumentProcessor, clean_text
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSOR_AVAILABLE = False

try:
    from embedding_utils import EmbeddingGenerator
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

# Token counting with fallback
def count_tokens(s: str) -> int:
    """Count tokens in text. Uses tiktoken if available, otherwise estimates with words."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(s))
    except ImportError:
        # Fallback: rough estimation using words
        # 1 token ≈ 0.75 words on average
        return int(len(s.split()) * 0.75)
    except Exception:
        # If tiktoken fails for any reason, fall back to word estimation
        return int(len(s.split()) * 0.75)

def read_file(path: str) -> str:
    """Read file content, supporting multiple formats."""
    if DOCUMENT_PROCESSOR_AVAILABLE:
        processor = DocumentProcessor()
        if processor.can_process(path):
            text, metadata = processor.extract_text(path)
            return clean_text(text)
    
    # Fallback to original method for markdown/text files
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_front_matter(md: str) -> Tuple[Dict, str]:
    """
    Very tolerant front-matter parser: expects content like
    ---\nkey: value\n...\n---\nbody...
    Returns (meta_dict, body_str). If none, returns ({}, full_text).
    """
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) >= 3:
            import yaml
            meta = (yaml.safe_load(parts[1]) or {}) if parts[1].strip() else {}
            body = parts[2].lstrip("\n")
            return meta, body
    return {}, md

def split_sentences(text: str) -> List[str]:
    # simple sentence/list splitter that also handles bullets; keeps newlines as spaces
    text = re.sub(r'\s+', ' ', text.strip())
    # treat bullet '•' as boundary; replace with period + space
    text = text.replace("•", ". ")
    # split by punctuation followed by space-capital/number or end
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    return [p.strip() for p in parts if p.strip()]

def make_chunks(text: str, target_tokens=280, overlap_tokens=40) -> List[str]:
    sents = split_sentences(text)
    chunks, cur, cur_toks = [], [], 0
    
    for s in sents:
        st = count_tokens(s)
        
        # If adding this sentence would exceed target, create a chunk
        if cur and cur_toks + st > target_tokens:
            chunk_text = " ".join(cur).strip()
            chunks.append(chunk_text)
            
            # Handle overlap: keep some sentences from the end
            if overlap_tokens > 0:
                # Calculate how many tokens to keep for overlap
                overlap_remaining = overlap_tokens
                overlap_sents = []
                
                # Start from the end and work backwards
                for sent in reversed(cur):
                    sent_tokens = count_tokens(sent)
                    if overlap_remaining >= sent_tokens:
                        overlap_sents.insert(0, sent)
                        overlap_remaining -= sent_tokens
                    else:
                        # If we can't fit the whole sentence, break
                        break
                
                # Start the next chunk with the overlap sentences
                cur = overlap_sents
                cur_toks = sum(count_tokens(s) for s in cur)
            else:
                cur, cur_toks = [], 0
        
        # Add current sentence to the chunk
        cur.append(s)
        cur_toks += st
    
    # Add the final chunk if there's content
    if cur:
        chunks.append(" ".join(cur).strip())
    
    return chunks

def build_items(body: str, base_meta: Dict, section: str, target_tokens=280, overlap_tokens=40, 
                generate_embeddings=False, embedding_model="all-MiniLM-L6-v2") -> List[Dict]:
    chunks = make_chunks(body, target_tokens, overlap_tokens)
    out = []
    
    # Generate embeddings if requested
    embeddings = None
    if generate_embeddings and EMBEDDING_AVAILABLE:
        try:
            generator = EmbeddingGenerator(embedding_model)
            embeddings = generator.generate_embeddings(chunks)
        except Exception as e:
            print(f"Warning: Could not generate embeddings: {e}")
    
    for i, ch in enumerate(chunks, 1):
        item = {
            "id": f"{base_meta.get('slug','doc')}:{section}:{i:03}",
            "text": ch,
            "metadata": {
                **base_meta,
                "section": section,
                "chunk_index": i,
                "updated": str(date.today())
            }
        }
        
        # Add embedding if available
        if embeddings is not None and i <= len(embeddings):
            item["embedding"] = embeddings[i-1].tolist()
        
        out.append(item)
    return out

def save_jsonl(items: List[Dict], out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} chunks → {out_path}")

def save_csv(items: List[Dict], out_path: str):
    """Save chunks as CSV for easy viewing."""
    import pandas as pd
    
    # Flatten metadata for CSV
    csv_data = []
    for item in items:
        row = {
            'id': item['id'],
            'text': item['text'],
            **item['metadata']
        }
        csv_data.append(row)
    
    df = pd.DataFrame(csv_data)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(items)} chunks → {out_path}")

def cmd_chunk(args):
    # Extract text from file
    if DOCUMENT_PROCESSOR_AVAILABLE:
        processor = DocumentProcessor()
        if processor.can_process(args.input):
            text, file_metadata = processor.extract_text(args.input)
            text = clean_text(text)
        else:
            text = read_file(args.input)
            file_metadata = {}
    else:
        text = read_file(args.input)
        file_metadata = {}
    
    # Parse front matter if it's a markdown file
    if args.input.lower().endswith('.md'):
        fm, body = parse_front_matter(text)
    else:
        fm, body = {}, text
    
    base_meta = {
        "title": fm.get("title", file_metadata.get("title", os.path.basename(args.input))),
        "slug": fm.get("slug", args.slug or os.path.splitext(os.path.basename(args.input))[0]),
        "jurisdiction": fm.get("jurisdiction","GB"),
        "doc_type": fm.get("doc_type","guidance"),
        "version": fm.get("version","1.0"),
        "effective_date": fm.get("effective_date",""),
        "review_date": fm.get("review_date",""),
        "owner": fm.get("owner","HSE-App"),
        "source_url": fm.get("source_url",""),
        "tags": fm.get("tags", []),
        "source_format": file_metadata.get("format", "unknown"),
    }
    
    section = args.section or fm.get("section","Main")
    items = build_items(body, base_meta, section, args.chunk_size, args.overlap, 
                       args.embeddings, args.embedding_model)
    
    # Save in requested format
    if args.out.endswith('.csv'):
        save_csv(items, args.out)
    else:
        save_jsonl(items, args.out)

def cmd_batch(args):
    if DOCUMENT_PROCESSOR_AVAILABLE:
        processor = DocumentProcessor()
        files_data = processor.batch_process(args.folder)
    else:
        # Fallback to original method
        files = [os.path.join(args.folder, f) for f in os.listdir(args.folder) 
                if f.lower().endswith((".md",".txt"))]
        files_data = [(f, read_file(f), {}) for f in sorted(files)]
    
    all_items = []
    for file_path, text, file_metadata in files_data:
        # Parse front matter if it's a markdown file
        if file_path.lower().endswith('.md'):
            fm, body = parse_front_matter(text)
        else:
            fm, body = {}, text
        
        base_meta = {
            "title": fm.get("title", file_metadata.get("title", os.path.basename(file_path))),
            "slug": fm.get("slug", (args.slug_prefix + "-" if args.slug_prefix else "") + 
                          os.path.splitext(os.path.basename(file_path))[0]),
            "jurisdiction": fm.get("jurisdiction","GB"),
            "doc_type": fm.get("doc_type","guidance"),
            "version": fm.get("version","1.0"),
            "effective_date": fm.get("effective_date",""),
            "review_date": fm.get("review_date",""),
            "owner": fm.get("owner","HSE-App"),
            "source_url": fm.get("source_url",""),
            "tags": fm.get("tags", []),
            "source_format": file_metadata.get("format", "unknown"),
        }
        
        section = fm.get("section", os.path.splitext(os.path.basename(file_path))[0])
        items = build_items(body, base_meta, section, args.chunk_size, args.overlap,
                           args.embeddings, args.embedding_model)
        all_items.extend(items)
    
    # Save in requested format
    if args.out.endswith('.csv'):
        save_csv(all_items, args.out)
    else:
        save_jsonl(all_items, args.out)

def main():
    ap = argparse.ArgumentParser(prog="rag_builder", description="Chunk documents for RAG.")
    sub = ap.add_subparsers()

    p1 = sub.add_parser("chunk", help="Chunk a single file")
    p1.add_argument("input", help="Path to document file (PDF, DOCX, TXT, MD, Excel)")
    p1.add_argument("--section", default=None, help="Section name override")
    p1.add_argument("--slug", default=None, help="Slug override")
    p1.add_argument("--chunk-size", type=int, default=280, help="Target tokens per chunk")
    p1.add_argument("--overlap", type=int, default=40, help="Overlap tokens between chunks")
    p1.add_argument("--out", required=True, help="Output file (.jsonl or .csv)")
    p1.add_argument("--embeddings", action="store_true", help="Generate embeddings")
    p1.add_argument("--embedding-model", default="all-MiniLM-L6-v2", 
                   help="Embedding model to use")
    p1.set_defaults(func=cmd_chunk)

    p2 = sub.add_parser("batch", help="Chunk all files in a folder")
    p2.add_argument("folder", help="Folder containing documents")
    p2.add_argument("--slug-prefix", default="", help="Prefix for slugs")
    p2.add_argument("--chunk-size", type=int, default=280)
    p2.add_argument("--overlap", type=int, default=40)
    p2.add_argument("--out", required=True, help="Output file (.jsonl or .csv)")
    p2.add_argument("--embeddings", action="store_true", help="Generate embeddings")
    p2.add_argument("--embedding-model", default="all-MiniLM-L6-v2", 
                   help="Embedding model to use")
    p2.set_defaults(func=cmd_batch)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
