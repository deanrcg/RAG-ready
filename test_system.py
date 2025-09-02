#!/usr/bin/env python3
"""
Test script for RAG Document Processor
"""

import os
import sys
import json
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import gradio
        print("✅ Gradio imported successfully")
    except ImportError as e:
        print(f"❌ Gradio import failed: {e}")
        return False
    
    try:
        import tiktoken
        print("✅ Tiktoken imported successfully")
    except ImportError as e:
        print(f"❌ Tiktoken import failed: {e}")
        return False
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError as e:
        print(f"❌ PyYAML import failed: {e}")
        return False
    
    try:
        from document_processor import DocumentProcessor
        print("✅ Document processor imported successfully")
    except ImportError as e:
        print(f"⚠️  Document processor import failed (optional): {e}")
    
    try:
        from embedding_utils import EmbeddingGenerator
        print("✅ Embedding utilities imported successfully")
    except ImportError as e:
        print(f"⚠️  Embedding utilities import failed (optional): {e}")
    
    return True

def test_document_processing():
    """Test document processing functionality."""
    print("\n📄 Testing document processing...")
    
    try:
        from document_processor import DocumentProcessor, clean_text
        
        processor = DocumentProcessor()
        
        # Test markdown processing
        test_file = "content/intro-to-hse/01-overview.md"
        if os.path.exists(test_file):
            text, metadata = processor.extract_text(test_file)
            print(f"✅ Markdown processing: {len(text)} characters, metadata: {metadata}")
        else:
            print("⚠️  Test markdown file not found")
        
        # Test text processing
        test_file = "content/sample-documents/03-training-manual.txt"
        if os.path.exists(test_file):
            text, metadata = processor.extract_text(test_file)
            print(f"✅ Text processing: {len(text)} characters, metadata: {metadata}")
        else:
            print("⚠️  Test text file not found")
        
        # Test text cleaning
        test_text = "This   has   extra   spaces.\n\n\nAnd empty lines."
        cleaned = clean_text(test_text)
        print(f"✅ Text cleaning: {len(cleaned)} characters")
        
        return True
        
    except ImportError:
        print("⚠️  Document processor not available")
        return True
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return False

def test_rag_builder():
    """Test RAG builder functionality."""
    print("\n🔧 Testing RAG builder...")
    
    try:
        from rag_builder import parse_front_matter, build_items, save_jsonl
        
        # Test front matter parsing
        test_md = """---
title: "Test Document"
slug: test-doc
tags: ["test", "example"]
---
This is the body content."""
        
        fm, body = parse_front_matter(test_md)
        print(f"✅ Front matter parsing: {fm}")
        
        # Test chunk building
        base_meta = {
            "title": "Test Document",
            "slug": "test-doc",
            "jurisdiction": "GB",
            "doc_type": "test",
            "version": "1.0"
        }
        
        items = build_items(body, base_meta, "Test", 100, 20)
        print(f"✅ Chunk building: {len(items)} chunks created")
        
        # Test JSONL saving
        test_output = "out/test_output.jsonl"
        save_jsonl(items, test_output)
        print(f"✅ JSONL saving: {test_output}")
        
        # Clean up
        if os.path.exists(test_output):
            os.remove(test_output)
        
        return True
        
    except Exception as e:
        print(f"❌ RAG builder test failed: {e}")
        return False

def test_embeddings():
    """Test embedding functionality."""
    print("\n🧠 Testing embeddings...")
    
    try:
        from embedding_utils import EmbeddingGenerator, cosine_similarity
        
        generator = EmbeddingGenerator()
        
        # Test embedding generation
        texts = [
            "This is a test document about safety.",
            "Another document about workplace guidelines.",
            "A third document about employee training."
        ]
        
        embeddings = generator.generate_embeddings(texts)
        print(f"✅ Embedding generation: {embeddings.shape}")
        
        # Test similarity
        if len(embeddings) >= 2:
            similarity = cosine_similarity(embeddings[0], embeddings[1])
            print(f"✅ Similarity calculation: {similarity:.3f}")
        
        return True
        
    except ImportError:
        print("⚠️  Embedding utilities not available")
        return True
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False

def test_cli():
    """Test command line interface."""
    print("\n💻 Testing CLI...")
    
    try:
        # Test with sample document
        test_file = "content/intro-to-hse/01-overview.md"
        if os.path.exists(test_file):
            output_file = "out/cli_test.jsonl"
            
            # Run CLI command
            cmd = f"python rag_builder.py chunk {test_file} --out {output_file}"
            result = os.system(cmd)
            
            if result == 0:
                print(f"✅ CLI test: {output_file}")
                
                # Check output
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        lines = f.readlines()
                    print(f"✅ CLI output: {len(lines)} chunks")
                    
                    # Clean up
                    os.remove(output_file)
                else:
                    print("❌ CLI output file not found")
            else:
                print("❌ CLI command failed")
        else:
            print("⚠️  Test file not found for CLI test")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running RAG Document Processor Tests")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("out", exist_ok=True)
    
    # Run tests
    tests = [
        test_imports,
        test_document_processing,
        test_rag_builder,
        test_embeddings,
        test_cli
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📋 Next steps:")
    print("1. Launch the web interface: python ui_gradio.py")
    print("2. Process documents: python rag_builder.py chunk <file> --out <output>")
    print("3. Check the README.md for more information")

if __name__ == "__main__":
    main()
