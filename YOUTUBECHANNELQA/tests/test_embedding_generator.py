"""
Test script for Embedding Generator module

This script tests the functionality of the embedding generator module.
"""

import os
import sys
import unittest
import numpy as np
from unittest.mock import patch, MagicMock

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings.embedding_generator import EmbeddingGenerator

class TestEmbeddingGenerator(unittest.TestCase):
    """Test cases for EmbeddingGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a patcher for the SentenceTransformer
        self.sentence_transformer_patcher = patch('src.embeddings.embedding_generator.SentenceTransformer')
        self.mock_sentence_transformer = self.sentence_transformer_patcher.start()
        
        # Create mock model
        self.mock_model = MagicMock()
        self.mock_model.get_sentence_embedding_dimension.return_value = 384
        self.mock_sentence_transformer.return_value = self.mock_model
        
        # Create EmbeddingGenerator instance
        self.generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    
    def tearDown(self):
        """Clean up after tests."""
        self.sentence_transformer_patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.generator.model_name, "all-MiniLM-L6-v2")
        self.assertEqual(self.generator.dimension, 384)
        self.mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    
    def test_generate_embedding(self):
        """Test generate_embedding method."""
        # Mock model encode method
        mock_embedding = np.array([0.1, 0.2, 0.3])
        self.mock_model.encode.return_value = mock_embedding
        
        # Call the method
        result = self.generator.generate_embedding("Test text")
        
        # Verify the results
        np.testing.assert_array_equal(result, mock_embedding)
        
        # Verify the model call
        self.mock_model.encode.assert_called_once_with("Test text", convert_to_numpy=True)
    
    def test_generate_embeddings(self):
        """Test generate_embeddings method."""
        # Mock model encode method
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ])
        self.mock_model.encode.return_value = mock_embeddings
        
        # Call the method
        texts = ["Text 1", "Text 2"]
        result = self.generator.generate_embeddings(texts, batch_size=32)
        
        # Verify the results
        np.testing.assert_array_equal(result, mock_embeddings)
        
        # Verify the model call
        self.mock_model.encode.assert_called_once_with(texts, batch_size=32, convert_to_numpy=True)
    
    def test_generate_embeddings_for_segments(self):
        """Test generate_embeddings_for_segments method."""
        # Mock model encode method
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ])
        self.mock_model.encode.return_value = mock_embeddings
        
        # Test segments
        segments = [
            {'text': 'Segment 1', 'start': 0.0, 'duration': 5.0},
            {'text': 'Segment 2', 'start': 5.0, 'duration': 4.0}
        ]
        
        # Call the method
        result = self.generator.generate_embeddings_for_segments(segments)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        np.testing.assert_array_equal(result[0]['embedding'], mock_embeddings[0])
        np.testing.assert_array_equal(result[1]['embedding'], mock_embeddings[1])
        self.assertEqual(result[0]['embedding_model'], "all-MiniLM-L6-v2")
        self.assertEqual(result[0]['embedding_dimension'], 384)
        
        # Verify the model call
        self.mock_model.encode.assert_called_once_with(['Segment 1', 'Segment 2'], batch_size=32, convert_to_numpy=True)
    
    def test_compute_similarity(self):
        """Test compute_similarity method."""
        # Test embeddings
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.0, 1.0, 0.0])
        embedding3 = np.array([1.0, 1.0, 0.0])
        
        # Call the method
        sim1_2 = self.generator.compute_similarity(embedding1, embedding2)
        sim1_3 = self.generator.compute_similarity(embedding1, embedding3)
        sim1_1 = self.generator.compute_similarity(embedding1, embedding1)
        
        # Verify the results
        self.assertAlmostEqual(sim1_2, 0.0)  # Orthogonal vectors
        self.assertAlmostEqual(sim1_3, 1.0 / np.sqrt(2))  # 45 degree angle
        self.assertAlmostEqual(sim1_1, 1.0)  # Same vector
    
    def test_get_model_info(self):
        """Test get_model_info method."""
        # Mock model methods
        self.mock_model.get_max_seq_length.return_value = 512
        
        # Call the method
        result = self.generator.get_model_info()
        
        # Verify the results
        self.assertEqual(result['model_name'], "all-MiniLM-L6-v2")
        self.assertEqual(result['dimension'], 384)
        self.assertEqual(result['max_sequence_length'], 512)

if __name__ == '__main__':
    unittest.main()
