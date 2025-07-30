"""
Embedding functionality for Ragify
"""

import numpy as np
from typing import List, Union, Dict, Any
from sentence_transformers import SentenceTransformer
from ragify.utils.logger import get_logger

logger = get_logger(__name__)


class TextEmbedder:
    """
    Handles text embedding using various models
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the text embedder
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """
        Load the embedding model
        """
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise RuntimeError(f"Could not load embedding model: {self.model_name}")
    
    def embed_text(self, text: Union[str, List[str]]) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Embed text using the loaded model
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Embedding(s) as numpy array(s)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            if isinstance(text, str):
                # Single text
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding
            else:
                # List of texts
                embeddings = self.model.encode(text, convert_to_numpy=True)
                return embeddings
        except Exception as e:
            logger.error(f"Error during embedding: {str(e)}")
            raise RuntimeError(f"Embedding failed: {str(e)}")
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed a list of text chunks
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            List of chunks with added 'embedding' field
        """
        if not chunks:
            return []
        
        # Extract text from chunks
        texts = [chunk["text"] for chunk in chunks]
        
        # Get embeddings
        embeddings = self.embed_text(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist() if isinstance(embeddings[i], np.ndarray) else embeddings[i]
        
        logger.info(f"Embedded {len(chunks)} chunks")
        return chunks
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model
        Returns:
            Embedding dimension
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Create a dummy embedding to get the dimension
        dummy_embedding = self.embed_text("test")
        return len(dummy_embedding)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        chunk_embeddings: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar chunks to a query embedding
        
        Args:
            query_embedding: Query embedding
            chunk_embeddings: List of chunks with embeddings
            top_k: Number of top results to return
            
        Returns:
            List of top-k most similar chunks with similarity scores
        """
        similarities = []
        
        for chunk in chunk_embeddings:
            if "embedding" not in chunk:
                logger.warning(f"Chunk {chunk.get('id', 'unknown')} has no embedding")
                continue
            
            chunk_emb = np.array(chunk["embedding"])
            similarity = self.compute_similarity(query_embedding, chunk_emb)
            
            similarities.append({
                **chunk,
                "similarity_score": similarity
            })
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return top-k results
        return similarities[:top_k] 