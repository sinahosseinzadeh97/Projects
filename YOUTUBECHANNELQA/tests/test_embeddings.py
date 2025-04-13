"""
Simple script to test if we can generate embeddings using sentence-transformers.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

def test_embeddings():
    """Test embedding generation with sentence-transformers."""
    try:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Model loaded successfully")
        print(f"Model info: {model}")
        
        # Test with a sample sentence
        test_sentences = [
            "what if you can validate a startup idea without actually building it",
            "chatting with Justin Mayers about startup validation",
            "testing embedding generation for YouTube transcripts"
        ]
        
        print("Generating embeddings for test sentences...")
        embeddings = model.encode(test_sentences)
        
        print(f"Successfully generated embeddings with shape: {embeddings.shape}")
        print(f"Example embedding vector (first 5 values): {embeddings[0][:5]}")
        
        # Calculate similarity between sentences
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        print(f"Similarity between first two sentences: {similarity:.4f}")
        
        return True
    except Exception as e:
        print(f"Error in embedding test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_embeddings()
    print(f"\nEmbedding test {'passed' if success else 'failed'}") 