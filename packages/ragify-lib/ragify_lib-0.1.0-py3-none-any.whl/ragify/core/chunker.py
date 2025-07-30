"""
Text chunking functionality for Ragify
"""

import re
from typing import List, Dict, Any
from ragify.utils.logger import get_logger

logger = get_logger(__name__)


class TextChunker:
    """
    Handles text chunking for RAG systems
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separator: str = "\n"
    ):
        """
        Initialize the text chunker
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
            separator: Character to use for splitting text
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunks with metadata
        """
        if not text.strip():
            return []
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split text into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk_metadata(
                    current_chunk.strip(), chunk_id
                ))
                chunk_id += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += sentence
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(self._create_chunk_metadata(
                current_chunk.strip(), chunk_id
            ))
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[\r\t]', ' ', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting - can be improved with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Add punctuation back
        sentences = [s + '.' for s in sentences if not s.endswith('.')]
        
        return sentences
    
    def _get_overlap_text(self, text: str) -> str:
        """
        Get the last part of text for overlap
        
        Args:
            text: Input text
            
        Returns:
            Overlap text
        """
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to break at word boundaries
        words = text.split()
        overlap_words = []
        current_length = 0
        
        for word in reversed(words):
            if current_length + len(word) + 1 <= self.chunk_overlap:
                overlap_words.insert(0, word)
                current_length += len(word) + 1
            else:
                break
        
        return ' '.join(overlap_words)
    
    def _create_chunk_metadata(self, text: str, chunk_id: int) -> Dict[str, Any]:
        """
        Create metadata for a chunk
        
        Args:
            text: Chunk text
            chunk_id: Unique identifier for the chunk
            
        Returns:
            Dictionary with chunk data and metadata
        """
        return {
            "id": f"chunk_{chunk_id}",
            "text": text,
            "length": len(text),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
    
    def chunk_text_recursive(self, text: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Recursively chunk text with decreasing chunk sizes
        
        Args:
            text: Input text
            max_depth: Maximum recursion depth
            
        Returns:
            List of chunks with metadata
        """
        if max_depth <= 0:
            return []
        
        # Try to chunk with current settings
        chunks = self.chunk_text(text)
        
        # If chunks are still too large, recursively chunk with smaller size
        if chunks and any(len(chunk["text"]) > self.chunk_size for chunk in chunks):
            logger.info(f"Recursively chunking with depth {max_depth}")
            
            # Reduce chunk size for next iteration
            smaller_chunker = TextChunker(
                chunk_size=self.chunk_size // 2,
                chunk_overlap=self.chunk_overlap // 2,
                separator=self.separator
            )
            
            all_chunks = []
            for chunk in chunks:
                if len(chunk["text"]) > self.chunk_size:
                    # Recursively chunk this chunk
                    sub_chunks = smaller_chunker.chunk_text_recursive(
                        chunk["text"], max_depth - 1
                    )
                    all_chunks.extend(sub_chunks)
                else:
                    all_chunks.append(chunk)
            
            return all_chunks
        
        return chunks 