#!/usr/bin/env python3
"""
Embedding utilities for RAG applications.
Provides easy integration with sentence-transformers and other embedding models.
"""

import numpy as np
from typing import List, Dict, Optional, Union
import json

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class EmbeddingGenerator:
    """Generate embeddings for text chunks using various models."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model to use
            device: Device to use ('cpu', 'cuda', etc.)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required. Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding
        """
        return self.generate_embeddings([text])[0]
    
    def add_embeddings_to_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to a list of document chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            List of chunks with added 'embedding' field
        """
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()
        
        return chunks

class VectorStore:
    """Simple vector store using FAISS for similarity search."""
    
    def __init__(self, dimension: int, index_type: str = "flat"):
        """
        Initialize vector store.
        
        Args:
            dimension: Dimension of embeddings
            index_type: Type of FAISS index ('flat', 'ivf', etc.)
        """
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is required. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.index_type = index_type
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.chunks = []
    
    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'embedding' field
        """
        if not chunks:
            return
        
        embeddings = np.array([chunk['embedding'] for chunk in chunks])
        self.index.add(embeddings)
        self.chunks.extend(chunks)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding
            k: Number of results to return
            
        Returns:
            List of similar chunks with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Reshape for single query
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                result = self.chunks[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results
    
    def save(self, filepath: str):
        """Save the vector store to disk."""
        faiss.write_index(self.index, f"{filepath}.index")
        
        # Save chunks separately
        with open(f"{filepath}.chunks.json", 'w') as f:
            json.dump(self.chunks, f, indent=2)
    
    def load(self, filepath: str):
        """Load the vector store from disk."""
        self.index = faiss.read_index(f"{filepath}.index")
        
        with open(f"{filepath}.chunks.json", 'r') as f:
            self.chunks = json.load(f)

def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """
    Normalize embeddings for cosine similarity.
    
    Args:
        embeddings: Raw embeddings
        
    Returns:
        Normalized embeddings
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
    return embeddings / norms

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score
    """
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return np.dot(a_norm, b_norm)

def batch_embed_with_progress(texts: List[str], model_name: str = "all-MiniLM-L6-v2", 
                            batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings with progress tracking.
    
    Args:
        texts: List of texts to embed
        model_name: Model name
        batch_size: Batch size for processing
        
    Returns:
        numpy array of embeddings
    """
    generator = EmbeddingGenerator(model_name)
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = generator.generate_embeddings(batch)
        embeddings.append(batch_embeddings)
        
        # Progress update
        progress = min((i + batch_size) / len(texts), 1.0)
        print(f"Embedding progress: {progress:.1%}")
    
    return np.vstack(embeddings)

# Predefined model configurations
MODEL_CONFIGS = {
    "fast": {
        "name": "all-MiniLM-L6-v2",
        "dimension": 384,
        "description": "Fast, good quality embeddings"
    },
    "balanced": {
        "name": "all-mpnet-base-v2",
        "dimension": 768,
        "description": "Good balance of speed and quality"
    },
    "high_quality": {
        "name": "all-MiniLM-L12-v2",
        "dimension": 384,
        "description": "Higher quality, slightly slower"
    }
}

if __name__ == "__main__":
    # Example usage
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        generator = EmbeddingGenerator()
        
        # Test with sample texts
        texts = [
            "This is a sample document about health and safety.",
            "Another document about workplace regulations.",
            "A third document about employee training."
        ]
        
        embeddings = generator.generate_embeddings(texts)
        print(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
        
        # Test similarity
        if len(embeddings) >= 2:
            similarity = cosine_similarity(embeddings[0], embeddings[1])
            print(f"Similarity between first two texts: {similarity:.3f}")
    else:
        print("sentence-transformers not available. Install with: pip install sentence-transformers")
