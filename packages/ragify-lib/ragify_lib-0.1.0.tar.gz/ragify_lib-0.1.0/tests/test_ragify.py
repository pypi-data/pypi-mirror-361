"""
Unit tests for Ragify
"""

import unittest
import json
from unittest.mock import Mock, patch
import numpy as np

from ragify import KaliRAG
from ragify.core.chunker import TextChunker
from ragify.core.embedder import TextEmbedder
from ragify.core.db_quadrant import QuadrantDB


class TestTextChunker(unittest.TestCase):
    """Test the TextChunker class"""
    
    def setUp(self):
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    
    def test_chunker_initialization(self):
        """Test chunker initialization"""
        self.assertEqual(self.chunker.chunk_size, 100)
        self.assertEqual(self.chunker.chunk_overlap, 20)
        self.assertEqual(self.chunker.separator, "\n")
    
    def test_chunker_invalid_overlap(self):
        """Test that invalid overlap raises ValueError"""
        with self.assertRaises(ValueError):
            TextChunker(chunk_size=50, chunk_overlap=60)
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  This   has\ttabs\nand\r\ncarriage returns  "
        cleaned = self.chunker._clean_text(dirty_text)
        self.assertEqual(cleaned, "This has tabs and carriage returns")
    
    def test_split_into_sentences(self):
        """Test sentence splitting"""
        text = "This is sentence one. This is sentence two! And sentence three?"
        sentences = self.chunker._split_into_sentences(text)
        self.assertEqual(len(sentences), 3)
        self.assertTrue(all(s.endswith('.') for s in sentences))
    
    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        chunks = self.chunker.chunk_text("")
        self.assertEqual(chunks, [])
        
        chunks = self.chunker.chunk_text("   ")
        self.assertEqual(chunks, [])
    
    def test_chunk_text_simple(self):
        """Test simple text chunking"""
        text = "This is a simple test sentence that should be chunked properly."
        chunks = self.chunker.chunk_text(text)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIn("id", chunk)
            self.assertIn("text", chunk)
            self.assertIn("length", chunk)
            self.assertLessEqual(len(chunk["text"]), 100)
    
    def test_chunk_text_recursive(self):
        """Test recursive chunking"""
        # Create a very long text
        long_text = "This is a very long sentence. " * 50
        chunks = self.chunker.chunk_text_recursive(long_text, max_depth=2)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk["text"]), 100)


class TestTextEmbedder(unittest.TestCase):
    """Test the TextEmbedder class"""
    
    @patch('sentence_transformers.SentenceTransformer')
    def setUp(self, mock_transformer):
        self.mock_model = Mock()
        mock_transformer.return_value = self.mock_model
        self.embedder = TextEmbedder("test-model")
    
    def test_embedder_initialization(self):
        """Test embedder initialization"""
        self.assertEqual(self.embedder.model_name, "test-model")
        self.assertIsNotNone(self.embedder.model)
    
    def test_embed_text_single(self):
        """Test embedding single text"""
        # Mock the encode method
        self.mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        result = self.embedder.embed_text("test text")
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), 3)
    
    def test_embed_text_multiple(self):
        """Test embedding multiple texts"""
        # Mock the encode method
        self.mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        result = self.embedder.embed_text(["text1", "text2"])
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (2, 2))
    
    def test_embed_chunks(self):
        """Test embedding chunks"""
        chunks = [
            {"id": "1", "text": "chunk 1"},
            {"id": "2", "text": "chunk 2"}
        ]
        
        # Mock the encode method
        self.mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        result = self.embedder.embed_chunks(chunks)
        
        self.assertEqual(len(result), 2)
        for chunk in result:
            self.assertIn("embedding", chunk)
    
    def test_compute_similarity(self):
        """Test similarity computation"""
        emb1 = np.array([1, 0, 0])
        emb2 = np.array([1, 0, 0])
        
        similarity = self.embedder.compute_similarity(emb1, emb2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
        
        # Test orthogonal vectors
        emb3 = np.array([0, 1, 0])
        similarity = self.embedder.compute_similarity(emb1, emb3)
        self.assertAlmostEqual(similarity, 0.0, places=5)


class TestQuadrantDB(unittest.TestCase):
    """Test the QuadrantDB class"""
    
    def setUp(self):
        self.db = QuadrantDB(
            api_key="test-key",
            host="https://test.quadrant.io",
            collection="test_collection"
        )
    
    def test_db_initialization(self):
        """Test database initialization"""
        self.assertEqual(self.db.api_key, "test-key")
        self.assertEqual(self.db.host, "https://test.quadrant.io")
        self.assertEqual(self.db.collection, "test_collection")
    
    def test_mock_store_embeddings(self):
        """Test mock storage"""
        chunks = [{"id": "1", "text": "test", "embedding": [0.1, 0.2]}]
        result = self.db._mock_store_embeddings(chunks)
        self.assertTrue(result)
    
    def test_mock_retrieve_similar(self):
        """Test mock retrieval"""
        query_embedding = [0.1, 0.2, 0.3]
        results = self.db._mock_retrieve_similar(query_embedding, top_k=2)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("id", result)
            self.assertIn("text", result)
            self.assertIn("similarity_score", result)


class TestKaliRAG(unittest.TestCase):
    """Test the main KaliRAG class"""
    
    @patch('ragify.core.embedder.SentenceTransformer')
    def setUp(self, mock_transformer):
        self.mock_model = Mock()
        mock_transformer.return_value = self.mock_model
        self.mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        self.rag = KaliRAG(
            embedding_model="test-model",
            chunk_size=100,
            chunk_overlap=20,
            db_config={"api_key": "test-key"}
        )
    
    def test_rag_initialization(self):
        """Test RAG initialization"""
        self.assertEqual(self.rag.embedding_model, "test-model")
        self.assertEqual(self.rag.chunk_size, 100)
        self.assertEqual(self.rag.chunk_overlap, 20)
        self.assertIsNotNone(self.rag.chunker)
        self.assertIsNotNone(self.rag.embedder)
        self.assertIsNotNone(self.rag.db)
    
    def test_create_store_embedding_success(self):
        """Test successful embedding creation and storage"""
        text = "This is a test text for embedding creation and storage."
        
        # Mock the database storage
        self.rag.db.store_embeddings = Mock(return_value=True)
        
        result = self.rag.create_store_embedding(text)
        
        self.assertTrue(result["success"])
        self.assertGreater(result["chunks_created"], 0)
        self.assertGreater(result["chunks_stored"], 0)
    
    def test_create_store_embedding_empty_text(self):
        """Test embedding creation with empty text"""
        result = self.rag.create_store_embedding("")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["chunks_created"], 0)
        self.assertEqual(result["chunks_stored"], 0)
    
    def test_retrieve_embedding_success(self):
        """Test successful embedding retrieval"""
        query = "test query"
        
        # Mock the database retrieval
        mock_results = [
            {
                "id": "1",
                "text": "test result 1",
                "similarity_score": 0.8,
                "metadata": {}
            }
        ]
        self.rag.db.retrieve_similar = Mock(return_value=mock_results)
        
        result = self.rag.retrieve_embedding(query, top_k=3)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["query"], query)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["total_results"], 1)
    
    def test_retrieve_embedding_no_results(self):
        """Test retrieval with no results"""
        query = "test query"
        
        # Mock empty results
        self.rag.db.retrieve_similar = Mock(return_value=[])
        
        result = self.rag.retrieve_embedding(query, top_k=3)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total_results"], 0)
    
    def test_get_info(self):
        """Test getting system information"""
        # Mock embedding dimension
        self.rag.embedder.get_embedding_dimension = Mock(return_value=384)
        self.rag.db.collection_exists = Mock(return_value=True)
        
        info = self.rag.get_info()
        
        self.assertIn("embedding_model", info)
        self.assertIn("embedding_dimension", info)
        self.assertIn("chunk_size", info)
        self.assertIn("chunk_overlap", info)
        self.assertIn("database", info)
    
    def test_reset_database(self):
        """Test database reset"""
        # Mock database operations
        self.rag.db.delete_collection = Mock(return_value=True)
        self.rag.db.create_collection = Mock(return_value=True)
        self.rag.embedder.get_embedding_dimension = Mock(return_value=384)
        
        result = self.rag.reset_database()
        
        self.assertTrue(result["success"])
        self.rag.db.delete_collection.assert_called_once()
        self.rag.db.create_collection.assert_called_once_with(dimension=384)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    @patch('ragify.core.embedder.SentenceTransformer')
    def test_full_workflow(self, mock_transformer):
        """Test the complete RAG workflow"""
        # Setup mocks
        mock_model = Mock()
        mock_transformer.return_value = mock_model
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        # Initialize RAG
        rag = KaliRAG(
            embedding_model="test-model",
            chunk_size=100,
            chunk_overlap=20,
            db_config={"api_key": "test-key"}
        )
        
        # Mock database operations
        rag.db.store_embeddings = Mock(return_value=True)
        rag.db.retrieve_similar = Mock(return_value=[
            {
                "id": "1",
                "text": "test result",
                "similarity_score": 0.8,
                "metadata": {}
            }
        ])
        
        # Test full workflow
        text = "This is a test document for the RAG workflow."
        
        # Step 1: Create and store embeddings
        store_result = rag.create_store_embedding(text)
        self.assertTrue(store_result["success"])
        
        # Step 2: Retrieve embeddings
        query = "test query"
        retrieve_result = rag.retrieve_embedding(query)
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["query"], query)


if __name__ == "__main__":
    unittest.main() 