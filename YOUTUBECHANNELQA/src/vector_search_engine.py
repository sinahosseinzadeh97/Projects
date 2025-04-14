"""
Vector Search Module

This module provides functionality to create and search FAISS indexes
for efficient similarity search of transcript segment embeddings.
"""

import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Any, Optional, Tuple

class VectorSearchEngine:
    """Class for vector similarity search using FAISS."""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize the vector search engine.
        
        Args:
            dimension (int, optional): Dimension of embedding vectors. Defaults to 384.
        """
        self.dimension = dimension
        self.index = None
        self.metadata = []
    
    def create_index(self, embeddings: np.ndarray, index_type: str = 'flat') -> None:
        """
        Create a FAISS index from embeddings.
        
        Args:
            embeddings (np.ndarray): Matrix of embedding vectors
            index_type (str, optional): Type of FAISS index to create. Defaults to 'flat'.
        """
        # Convert embeddings to float32 (required by FAISS)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create appropriate index based on type
        if index_type == 'flat':
            # Exact search (L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)
        elif index_type == 'ivf':
            # Approximate search with inverted file index
            # Requires at least 100x more vectors than clusters for good results
            nlist = min(int(len(embeddings) / 10), 100)  # Number of clusters
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            # Need to train IVF index
            self.index.train(embeddings)
        elif index_type == 'hnsw':
            # Hierarchical Navigable Small World graph
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors per node
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Add vectors to the index
        self.index.add(embeddings)
        
        print(f"Created FAISS index with {self.index.ntotal} vectors of dimension {self.dimension}")
    
    def add_embeddings(self, embeddings: np.ndarray, metadata_list: List[Dict[str, Any]]) -> None:
        """
        Add embeddings and their metadata to the index.
        
        Args:
            embeddings (np.ndarray): Matrix of embedding vectors
            metadata_list (List[Dict[str, Any]]): List of metadata dictionaries for each embedding
        """
        if self.index is None:
            self.create_index(embeddings)
        else:
            # Convert embeddings to float32 (required by FAISS)
            embeddings = np.array(embeddings).astype('float32')
            self.index.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata_list)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Search for similar vectors in the index.
        
        Args:
            query_embedding (np.ndarray): Query embedding vector
            k (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]: 
                Distances, indices, and metadata of similar vectors
        """
        if self.index is None:
            raise ValueError("Index has not been created yet")
        
        # Convert query to float32 and reshape
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Get metadata for results
        result_metadata = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                result_metadata.append(self.metadata[idx])
            else:
                result_metadata.append({})
        
        return distances[0], indices[0], result_metadata
    
    def save(self, index_path: str, metadata_path: str) -> None:
        """
        Save the index and metadata to disk.
        
        Args:
            index_path (str): Path to save the FAISS index
            metadata_path (str): Path to save the metadata
        """
        if self.index is None:
            raise ValueError("Index has not been created yet")
        
        # Save the index
        faiss.write_index(self.index, index_path)
        
        # Save the metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"Saved index to {index_path} and metadata to {metadata_path}")
    
    def load(self, index_path: str, metadata_path: str) -> None:
        """
        Load the index and metadata from disk.
        
        Args:
            index_path (str): Path to the FAISS index
            metadata_path (str): Path to the metadata
        """
        # Load the index
        self.index = faiss.read_index(index_path)
        self.dimension = self.index.d
        
        # Load the metadata
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        print(f"Loaded index from {index_path} with {self.index.ntotal} vectors of dimension {self.dimension}")
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get information about the current index.
        
        Returns:
            Dict[str, Any]: Index information
        """
        if self.index is None:
            return {'status': 'not_created'}
        
        return {
            'status': 'created',
            'type': type(self.index).__name__,
            'dimension': self.dimension,
            'num_vectors': self.index.ntotal,
            'num_metadata': len(self.metadata)
        }
