"""
Quadrant vector database integration for Ragify
"""

import json
from typing import List, Dict, Any, Optional
from ragify.utils.logger import get_logger

logger = get_logger(__name__)


class QuadrantDB:
    """
    Quadrant vector database integration
    """
    
    def __init__(
        self,
        api_key: str,
        host: str = "https://api.quadrant.io",
        collection: str = "ragify_docs"
    ):
        """
        Initialize Quadrant database connection
        
        Args:
            api_key: Quadrant API key
            host: Quadrant API host
            collection: Collection name
        """
        self.api_key = api_key
        self.host = host
        self.collection = collection
        self.client = None
        
        # Try to import quadrant-sdk
        try:
            import quadrant
            self.client = quadrant.Client(api_key=api_key, host=host)
            logger.info(f"Connected to Quadrant at {host}")
        except ImportError:
            logger.warning("quadrant-sdk not installed. Using mock mode.")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to connect to Quadrant: {str(e)}")
            self.client = None
    
    def store_embeddings(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store embeddings in Quadrant
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            logger.warning("No chunks to store")
            return False
        
        if self.client is None:
            logger.warning("Quadrant client not available. Using mock storage.")
            return self._mock_store_embeddings(chunks)
        
        try:
            # Check if collection exists, create if it doesn't
            if not self.collection_exists():
                logger.info(f"Collection {self.collection} does not exist. Creating...")
                embedding_dim = len(chunks[0]["embedding"]) if chunks and "embedding" in chunks[0] else 384
                if not self.create_collection(dimension=embedding_dim):
                    logger.error(f"Failed to create collection {self.collection}")
                    return False
                logger.info(f"Successfully created collection {self.collection}")
            
            # Prepare data for Quadrant
            vectors = []
            for chunk in chunks:
                if "embedding" not in chunk:
                    logger.warning(f"Chunk {chunk.get('id', 'unknown')} has no embedding")
                    continue
                
                vector_data = {
                    "id": chunk["id"],
                    "vector": chunk["embedding"],
                    "metadata": {
                        "text": chunk["text"],
                        "length": chunk.get("length", 0),
                        "chunk_size": chunk.get("chunk_size", 0),
                        "chunk_overlap": chunk.get("chunk_overlap", 0)
                    }
                }
                vectors.append(vector_data)
            
            # Store in Quadrant
            self.client.upsert(
                collection_name=self.collection,
                vectors=vectors
            )
            
            logger.info(f"Stored {len(vectors)} embeddings in Quadrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embeddings in Quadrant: {str(e)}")
            return False
    
    def retrieve_similar(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar embeddings from Quadrant
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks with metadata
        """
        if self.client is None:
            logger.warning("Quadrant client not available. Using mock retrieval.")
            return self._mock_retrieve_similar(query_embedding, top_k, similarity_threshold)
        
        try:
            # Query Quadrant
            results = self.client.query(
                collection_name=self.collection,
                query_vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Process results
            similar_chunks = []
            for result in results:
                if result.score >= similarity_threshold:
                    chunk_data = {
                        "id": result.id,
                        "text": result.metadata.get("text", ""),
                        "similarity_score": result.score,
                        "metadata": result.metadata
                    }
                    similar_chunks.append(chunk_data)
            
            logger.info(f"Retrieved {len(similar_chunks)} similar chunks from Quadrant")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Failed to retrieve from Quadrant: {str(e)}")
            return []
    
    def delete_collection(self) -> bool:
        """
        Delete the collection from Quadrant
        
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Quadrant client not available. Cannot delete collection.")
            return False
        
        try:
            self.client.delete_collection(self.collection)
            logger.info(f"Deleted collection: {self.collection}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False
    
    def collection_exists(self) -> bool:
        """
        Check if the collection exists
        
        Returns:
            True if collection exists, False otherwise
        """
        if self.client is None:
            logger.warning("Quadrant client not available. Assuming collection exists.")
            return True
        
        try:
            collections = self.client.list_collections()
            return self.collection in [col.name for col in collections]
        except Exception as e:
            logger.error(f"Failed to check collection existence: {str(e)}")
            return False
    
    def create_collection(self, dimension: int = 384) -> bool:
        """
        Create a new collection
        
        Args:
            dimension: Embedding dimension
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Quadrant client not available. Cannot create collection.")
            return False
        
        try:
            self.client.create_collection(
                name=self.collection,
                dimension=dimension
            )
            logger.info(f"Created collection: {self.collection} with dimension {dimension}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    # Mock methods for testing without Quadrant SDK
    def _mock_store_embeddings(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Mock storage for testing
        """
        logger.info(f"Mock: Stored {len(chunks)} embeddings")
        return True
    
    def _mock_retrieve_similar(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Mock retrieval for testing
        """
        logger.info(f"Mock: Retrieved {top_k} similar chunks")
        
        # Return more realistic mock data with actual text content
        mock_texts = [
            "Artificial Intelligence (AI) represents one of the most transformative technological revolutions of the 21st century, fundamentally altering how we approach problem-solving, decision-making, and human-computer interaction.",
            "The field encompasses a broad spectrum of technologies, from machine learning algorithms that can recognize patterns in vast datasets to natural language processing systems that can understand and generate human language with remarkable accuracy.",
            "Deep learning, a subset of machine learning, has particularly revolutionized AI capabilities by enabling systems to learn hierarchical representations of data through neural networks with multiple layers.",
            "The applications of AI are virtually limitless, spanning industries from healthcare and finance to transportation and entertainment.",
            "In healthcare, AI systems can analyze medical images to detect diseases like cancer with accuracy rates that rival or exceed human radiologists."
        ]
        
        return [
            {
                "id": f"mock_chunk_{i}",
                "text": mock_texts[i % len(mock_texts)],
                "similarity_score": 0.9 - (i * 0.15),
                "metadata": {"length": len(mock_texts[i % len(mock_texts)]), "chunk_size": 512}
            }
            for i in range(min(top_k, len(mock_texts)))
        ] 