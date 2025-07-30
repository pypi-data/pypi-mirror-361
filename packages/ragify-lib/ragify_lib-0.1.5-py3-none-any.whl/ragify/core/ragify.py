"""
Main RAG class for Ragify
"""

import json
from typing import Dict, Any, List, Optional
from ragify.core.chunker import TextChunker
from ragify.core.embedder import TextEmbedder
from ragify.core.db_quadrant import QuadrantDB
from ragify.config.defaults import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD
)
from ragify.utils.logger import get_logger

logger = get_logger(__name__)


class KaliRAG:
    """
    Main RAG class that orchestrates text chunking, embedding, and retrieval
    """
    
    def __init__(
        self,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        db_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize KaliRAG
        
        Args:
            embedding_model: Name of the embedding model to use
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
            db_config: Database configuration dictionary
            **kwargs: Additional arguments passed to database
        """
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.embedder = TextEmbedder(model_name=embedding_model)
        
        # Initialize database with default config
        if db_config is None:
            db_config = {}
        
        self.db = QuadrantDB(
            api_key=db_config.get("api_key", "mock_key"),
            host=db_config.get("host", "https://api.quadrant.io"),
            collection=db_config.get("collection", "ragify_docs")
        )
        
        # Store additional configuration
        self.config = {
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "db_config": db_config,
            **kwargs
        }
        
        logger.info(f"Initialized KaliRAG with model: {embedding_model}")
    
    def configure_database(
        self,
        api_key: str,
        host: str = "https://api.quadrant.io",
        port: Optional[int] = None,
        collection: str = "ragify_docs"
    ) -> bool:
        """
        Configure the database connection with user-provided settings
        
        Args:
            api_key: Quadrant API key
            host: Quadrant host URL (e.g., "https://api.quadrant.io")
            port: Optional port number (will be appended to host if provided)
            collection: Collection name for storing embeddings
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Construct full host URL with port if provided
            full_host = host
            if port:
                # Remove trailing slash from host if present
                if full_host.endswith('/'):
                    full_host = full_host[:-1]
                full_host = f"{full_host}:{port}"
            
            # Create new database instance with user configuration
            self.db = QuadrantDB(
                api_key=api_key,
                host=full_host,
                collection=collection
            )
            
            # Update config
            self.config["db_config"] = {
                "api_key": api_key,
                "host": full_host,
                "collection": collection
            }
            
            logger.info(f"Database configured: {full_host}/{collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure database: {str(e)}")
            return False
    
    def configure_embedding_model(self, model_name: str) -> bool:
        """
        Configure the embedding model
        
        Args:
            model_name: Name of the embedding model to use
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Create new embedder with specified model
            self.embedder = TextEmbedder(model_name=model_name)
            self.embedding_model = model_name
            
            # Update config
            self.config["embedding_model"] = model_name
            
            logger.info(f"Embedding model configured: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure embedding model: {str(e)}")
            return False
    
    def configure_chunking(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> bool:
        """
        Configure text chunking parameters
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            if chunk_overlap >= chunk_size:
                raise ValueError("chunk_overlap must be less than chunk_size")
            
            # Create new chunker with specified parameters
            self.chunker = TextChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
            
            # Update config
            self.config["chunk_size"] = chunk_size
            self.config["chunk_overlap"] = chunk_overlap
            
            logger.info(f"Chunking configured: size={chunk_size}, overlap={chunk_overlap}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure chunking: {str(e)}")
            return False
    
    def create_store_embedding(
        self,
        raw_text: str,
        use_recursive_chunking: bool = False,
        max_recursion_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Create embeddings from raw text and store them in the database
        
        Args:
            raw_text: Raw text to process
            use_recursive_chunking: Whether to use recursive chunking
            max_recursion_depth: Maximum recursion depth for chunking
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info("Starting embedding creation and storage process")
            
            # Step 1: Chunk the text
            if use_recursive_chunking:
                chunks = self.chunker.chunk_text_recursive(
                    raw_text, max_depth=max_recursion_depth
                )
            else:
                chunks = self.chunker.chunk_text(raw_text)
            
            if not chunks:
                logger.warning("No chunks created from input text")
                return {
                    "success": False,
                    "error": "No chunks created from input text",
                    "chunks_created": 0,
                    "chunks_stored": 0
                }
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 2: Create embeddings
            embedded_chunks = self.embedder.embed_chunks(chunks)
            
            if not embedded_chunks:
                logger.error("Failed to create embeddings")
                return {
                    "success": False,
                    "error": "Failed to create embeddings",
                    "chunks_created": len(chunks),
                    "chunks_stored": 0
                }
            
            logger.info(f"Created embeddings for {len(embedded_chunks)} chunks")
            
            # Step 3: Store in database
            storage_success = self.db.store_embeddings(embedded_chunks)
            
            if not storage_success:
                logger.error("Failed to store embeddings in database")
                return {
                    "success": False,
                    "error": "Failed to store embeddings in database",
                    "chunks_created": len(chunks),
                    "chunks_stored": 0
                }
            
            logger.info("Successfully completed embedding creation and storage")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "chunks_stored": len(embedded_chunks),
                "embedding_model": self.embedding_model,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
            
        except Exception as e:
            logger.error(f"Error in create_store_embedding: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks_created": 0,
                "chunks_stored": 0
            }
    
    def retrieve_embedding(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Retrieve relevant embeddings based on a query
        
        Args:
            query: Query string
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            Dictionary with retrieval results
        """
        try:
            logger.info(f"Retrieving embeddings for query: {query[:50]}...")
            
            # Step 1: Create query embedding
            query_embedding = self.embedder.embed_text(query)
            
            if query_embedding is None:
                logger.error("Failed to create query embedding")
                return {
                    "success": False,
                    "error": "Failed to create query embedding",
                    "results": [],
                    "query": query
                }
            
            # Step 2: Retrieve similar embeddings from database
            similar_chunks = self.db.retrieve_similar(
                query_embedding=query_embedding.tolist(),
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            logger.info(f"Retrieved {len(similar_chunks)} similar chunks")
            
            # Step 3: Format results
            results = []
            for chunk in similar_chunks:
                result = {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "similarity_score": chunk["similarity_score"],
                    "metadata": chunk.get("metadata", {})
                }
                results.append(result)
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "top_k": top_k,
                "similarity_threshold": similarity_threshold
            }
            
        except Exception as e:
            logger.error(f"Error in retrieve_embedding: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the current RAG configuration
        
        Returns:
            Dictionary with configuration information
        """
        try:
            embedding_dim = self.embedder.get_embedding_dimension()
            collection_exists = self.db.collection_exists()
            
            return {
                "embedding_model": self.embedding_model,
                "embedding_dimension": embedding_dim,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "database": {
                    "type": "quadrant",
                    "host": self.db.host,
                    "collection": self.db.collection,
                    "collection_exists": collection_exists
                },
                "config": self.config
            }
        except Exception as e:
            logger.error(f"Error getting info: {str(e)}")
            return {
                "error": str(e),
                "config": self.config
            }
    
    def reset_database(self) -> Dict[str, Any]:
        """
        Reset the database by deleting and recreating the collection
        
        Returns:
            Dictionary with reset results
        """
        try:
            logger.info("Resetting database")
            
            # Delete existing collection
            delete_success = self.db.delete_collection()
            
            # Create new collection
            embedding_dim = self.embedder.get_embedding_dimension()
            create_success = self.db.create_collection(dimension=embedding_dim)
            
            if delete_success and create_success:
                logger.info("Successfully reset database")
                return {
                    "success": True,
                    "message": "Database reset successfully"
                }
            else:
                logger.error("Failed to reset database")
                return {
                    "success": False,
                    "error": "Failed to reset database"
                }
                
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 