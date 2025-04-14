"""
Test script for Vector Search Engine module

This script tests the functionality of the vector search engine module.
"""

import os
import sys
import unittest
import numpy as np
import pickle
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_search.vector_search_engine import VectorSearchEngine

class TestVectorSearchEngine(unittest.TestCase):
    """Test cases for VectorSearchEngine class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a patcher for faiss
        self.faiss_patcher = patch('src.vector_search.vector_search_engine.faiss')
        self.mock_faiss = self.faiss_patcher.start()
        
        # Create mock index
        self.mock_index = MagicMock()
        self.mock_index.d = 384
        self.mock_index.ntotal = 100
        
        # Create VectorSearchEngine instance
        self.search_engine = VectorSearchEngine(dimension=384)
    
    def tearDown(self):
        """Clean up after tests."""
        self.faiss_patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.search_engine.dimension, 384)
        self.assertIsNone(self.search_engine.index)
        self.assertEqual(self.search_engine.metadata, [])
    
    def test_create_index_flat(self):
        """Test create_index method with flat index type."""
        # Mock faiss.IndexFlatL2
        mock_flat_index = MagicMock()
        self.mock_faiss.IndexFlatL2.return_value = mock_flat_index
        
        # Test embeddings
        embeddings = np.random.random((10, 384)).astype('float32')
        
        # Call the method
        self.search_engine.create_index(embeddings, index_type='flat')
        
        # Verify the results
        self.assertEqual(self.search_engine.index, mock_flat_index)
        
        # Verify faiss calls
        self.mock_faiss.IndexFlatL2.assert_called_once_with(384)
        mock_flat_index.add.assert_called_once()
        np.testing.assert_array_equal(mock_flat_index.add.call_args[0][0], embeddings)
    
    def test_create_index_ivf(self):
        """Test create_index method with ivf index type."""
        # Mock faiss.IndexFlatL2 and faiss.IndexIVFFlat
        mock_quantizer = MagicMock()
        mock_ivf_index = MagicMock()
        self.mock_faiss.IndexFlatL2.return_value = mock_quantizer
        self.mock_faiss.IndexIVFFlat.return_value = mock_ivf_index
        
        # Test embeddings
        embeddings = np.random.random((100, 384)).astype('float32')
        
        # Call the method
        self.search_engine.create_index(embeddings, index_type='ivf')
        
        # Verify the results
        self.assertEqual(self.search_engine.index, mock_ivf_index)
        
        # Verify faiss calls
        self.mock_faiss.IndexFlatL2.assert_called_once_with(384)
        self.mock_faiss.IndexIVFFlat.assert_called_once_with(mock_quantizer, 384, 10)
        mock_ivf_index.train.assert_called_once()
        np.testing.assert_array_equal(mock_ivf_index.train.call_args[0][0], embeddings)
        mock_ivf_index.add.assert_called_once()
        np.testing.assert_array_equal(mock_ivf_index.add.call_args[0][0], embeddings)
    
    def test_create_index_hnsw(self):
        """Test create_index method with hnsw index type."""
        # Mock faiss.IndexHNSWFlat
        mock_hnsw_index = MagicMock()
        self.mock_faiss.IndexHNSWFlat.return_value = mock_hnsw_index
        
        # Test embeddings
        embeddings = np.random.random((10, 384)).astype('float32')
        
        # Call the method
        self.search_engine.create_index(embeddings, index_type='hnsw')
        
        # Verify the results
        self.assertEqual(self.search_engine.index, mock_hnsw_index)
        
        # Verify faiss calls
        self.mock_faiss.IndexHNSWFlat.assert_called_once_with(384, 32)
        mock_hnsw_index.add.assert_called_once()
        np.testing.assert_array_equal(mock_hnsw_index.add.call_args[0][0], embeddings)
    
    def test_create_index_invalid_type(self):
        """Test create_index method with invalid index type."""
        # Test embeddings
        embeddings = np.random.random((10, 384)).astype('float32')
        
        # Call the method with invalid type
        with self.assertRaises(ValueError):
            self.search_engine.create_index(embeddings, index_type='invalid')
    
    def test_add_embeddings_new_index(self):
        """Test add_embeddings method with no existing index."""
        # Mock create_index method
        self.search_engine.create_index = MagicMock()
        
        # Test data
        embeddings = np.random.random((10, 384)).astype('float32')
        metadata_list = [{'id': i, 'text': f'Text {i}'} for i in range(10)]
        
        # Call the method
        self.search_engine.add_embeddings(embeddings, metadata_list)
        
        # Verify the results
        self.search_engine.create_index.assert_called_once_with(embeddings)
        self.assertEqual(self.search_engine.metadata, metadata_list)
    
    def test_add_embeddings_existing_index(self):
        """Test add_embeddings method with existing index."""
        # Set up existing index
        self.search_engine.index = MagicMock()
        
        # Test data
        embeddings = np.random.random((10, 384)).astype('float32')
        metadata_list = [{'id': i, 'text': f'Text {i}'} for i in range(10)]
        
        # Call the method
        self.search_engine.add_embeddings(embeddings, metadata_list)
        
        # Verify the results
        self.search_engine.index.add.assert_called_once()
        np.testing.assert_array_equal(self.search_engine.index.add.call_args[0][0], embeddings)
        self.assertEqual(self.search_engine.metadata, metadata_list)
    
    def test_search(self):
        """Test search method."""
        # Set up existing index
        self.search_engine.index = MagicMock()
        self.search_engine.index.search.return_value = (
            np.array([[0.1, 0.2, 0.3]]),  # Distances
            np.array([[0, 1, 2]])         # Indices
        )
        
        # Set up metadata
        self.search_engine.metadata = [
            {'id': 0, 'text': 'Text 0'},
            {'id': 1, 'text': 'Text 1'},
            {'id': 2, 'text': 'Text 2'},
            {'id': 3, 'text': 'Text 3'}
        ]
        
        # Test query
        query_embedding = np.random.random(384).astype('float32')
        
        # Call the method
        distances, indices, metadata = self.search_engine.search(query_embedding, k=3)
        
        # Verify the results
        np.testing.assert_array_equal(distances, np.array([0.1, 0.2, 0.3]))
        np.testing.assert_array_equal(indices, np.array([0, 1, 2]))
        self.assertEqual(len(metadata), 3)
        self.assertEqual(metadata[0]['id'], 0)
        self.assertEqual(metadata[1]['id'], 1)
        self.assertEqual(metadata[2]['id'], 2)
        
        # Verify index call
        self.search_engine.index.search.assert_called_once()
        np.testing.assert_array_equal(self.search_engine.index.search.call_args[0][0].shape, (1, 384))
        self.assertEqual(self.search_engine.index.search.call_args[0][1], 3)
    
    def test_search_no_index(self):
        """Test search method with no index."""
        # Test query
        query_embedding = np.random.random(384).astype('float32')
        
        # Call the method
        with self.assertRaises(ValueError):
            self.search_engine.search(query_embedding, k=3)
    
    @patch('src.vector_search.vector_search_engine.pickle.dump')
    def test_save(self, mock_pickle_dump):
        """Test save method."""
        # Set up existing index
        self.search_engine.index = MagicMock()
        self.search_engine.metadata = [{'id': i} for i in range(3)]
        
        # Mock open
        mock_open_file = mock_open()
        with patch('builtins.open', mock_open_file):
            # Call the method
            self.search_engine.save('index.bin', 'metadata.pkl')
        
        # Verify faiss call
        self.mock_faiss.write_index.assert_called_once_with(self.search_engine.index, 'index.bin')
        
        # Verify pickle call
        mock_pickle_dump.assert_called_once()
        self.assertEqual(mock_pickle_dump.call_args[0][0], self.search_engine.metadata)
    
    def test_save_no_index(self):
        """Test save method with no index."""
        # Call the method
        with self.assertRaises(ValueError):
            self.search_engine.save('index.bin', 'metadata.pkl')
    
    @patch('src.vector_search.vector_search_engine.pickle.load')
    def test_load(self, mock_pickle_load):
        """Test load method."""
        # Mock faiss.read_index
        self.mock_faiss.read_index.return_value = self.mock_index
        
        # Mock pickle.load
        mock_metadata = [{'id': i} for i in range(3)]
        mock_pickle_load.return_value = mock_metadata
        
        # Mock open
        mock_open_file = mock_open()
        with patch('builtins.open', mock_open_file):
            # Call the method
            self.search_engine.load('index.bin', 'metadata.pkl')
        
        # Verify the results
        self.assertEqual(self.search_engine.index, self.mock_index)
        self.assertEqual(self.search_engine.dimension, 384)
        self.assertEqual(self.search_engine.metadata, mock_metadata)
        
        # Verify faiss call
        self.mock_faiss.read_index.assert_called_once_with('index.bin')
    
    def test_get_index_info_no_index(self):
        """Test get_index_info method with no index."""
        # Call the method
        result = self.search_engine.get_index_info()
        
        # Verify the results
        self.assertEqual(result['status'], 'not_created')
    
    def test_get_index_info_with_index(self):
        """Test get_index_info method with existing index."""
        # Set up existing index
        self.search_engine.index = self.mock_index
        self.search_engine.metadata = [{'id': i} for i in range(3)]
        
        # Call the method
        result = self.search_engine.get_index_info()
        
        # Verify the results
        self.assertEqual(result['status'], 'created')
        self.assertEqual(result['dimension'], 384)
        self.assertEqual(result['num_vectors'], 100)
        self.assertEqual(result['num_metadata'], 3)

if __name__ == '__main__':
    unittest.main()
