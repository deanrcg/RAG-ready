#!/usr/bin/env python3
"""
Test script to verify chunking logic
"""

from rag_builder import make_chunks, count_tokens, split_sentences

def test_chunking():
    """Test the chunking logic with sample text."""
    
    # Longer sample text with multiple sentences
    sample_text = """
    This is the first sentence of a longer document. This is the second sentence with more words and content to make it substantial. 
    Here is a third sentence that continues the text and provides additional context for the reader. The fourth sentence adds more content and helps build the narrative.
    Fifth sentence follows naturally and maintains the flow of the document. Sixth sentence maintains the flow and adds variety to the text structure. 
    Seventh sentence continues the pattern and provides more information. Eighth sentence adds variety and keeps the reader engaged.
    Ninth sentence keeps going and expands on the previous ideas. Tenth sentence wraps up this section and provides a conclusion.
    Eleventh sentence starts a new thought and introduces a different topic. Twelfth sentence develops the idea further and provides examples.
    Thirteenth sentence provides more detail and explains the concepts clearly. Fourteenth sentence concludes the paragraph and summarizes the main points.
    Fifteenth sentence begins a new section and introduces fresh content. Sixteenth sentence expands on the topic and provides additional context.
    Seventeenth sentence adds context and helps the reader understand the material better. Eighteenth sentence provides examples and illustrates the concepts.
    Nineteenth sentence summarizes the point and reinforces the main ideas. Twentieth sentence concludes the text and provides a final thought.
    Twenty-first sentence continues the pattern and adds more content. Twenty-second sentence maintains consistency and builds on previous information.
    Twenty-third sentence provides additional details and expands the scope. Twenty-fourth sentence concludes this section and prepares for the next.
    Twenty-fifth sentence introduces new concepts and keeps the content fresh. Twenty-sixth sentence develops these ideas and provides context.
    Twenty-seventh sentence adds more information and helps clarify the points. Twenty-eighth sentence summarizes the section and provides closure.
    Twenty-ninth sentence begins the final section and introduces concluding thoughts. Thirtieth sentence wraps up the document and provides final insights.
    """
    
    print("🧪 Testing chunking logic...")
    print(f"Sample text length: {len(sample_text)} characters")
    print(f"Sample text tokens: {count_tokens(sample_text)}")
    
    # Test sentence splitting
    sentences = split_sentences(sample_text)
    print(f"Split into {len(sentences)} sentences:")
    for i, sent in enumerate(sentences[:5], 1):  # Show first 5
        print(f"  {i}. {sent[:80]}... ({count_tokens(sent)} tokens)")
    if len(sentences) > 5:
        print(f"  ... and {len(sentences) - 5} more sentences")
    
    # Test different chunk sizes
    test_cases = [
        (100, 20, "Small chunks"),
        (200, 40, "Medium chunks"),
        (300, 20, "Large chunks (your case)")
    ]
    
    for target_tokens, overlap_tokens, description in test_cases:
        print(f"\n📊 {description}:")
        print(f"  Target: {target_tokens} tokens, Overlap: {overlap_tokens} tokens")
        
        chunks = make_chunks(sample_text, target_tokens, overlap_tokens)
        
        print(f"  Generated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            chunk_tokens = count_tokens(chunk)
            print(f"    Chunk {i}: {chunk_tokens} tokens, {len(chunk)} chars")
            print(f"      Preview: {chunk[:100]}...")
            
            # Verify no chunk contains the entire text
            if len(chunk) > len(sample_text) * 0.8:  # More than 80% of original
                print(f"    ⚠️  WARNING: Chunk {i} seems too large!")
        
        # Check for overlap between consecutive chunks
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                chunk1_words = set(chunks[i].split())
                chunk2_words = set(chunks[i + 1].split())
                overlap_words = chunk1_words.intersection(chunk2_words)
                overlap_ratio = len(overlap_words) / len(chunk1_words) if chunk1_words else 0
                print(f"    Overlap between chunks {i+1} and {i+2}: {len(overlap_words)} words ({overlap_ratio:.1%})")

if __name__ == "__main__":
    test_chunking()
