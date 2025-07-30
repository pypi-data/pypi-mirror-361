# 🧾 Ragify

A simple, clean Python library to abstract away the complexity of Retrieval-Augmented Generation (RAG) by allowing developers to create embeddings and retrieve them using minimal setup.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ragify.svg)](https://badge.fury.io/py/ragify)

## 🚀 Quick Start

### Method 1: Initialize with Configuration Dictionary

```python
from ragify import KaliRAG

# Initialize with your configuration
config = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "db_config": {
        "api_key": "your-quadrant-api-key",
        "host": "https://api.quadrant.io",
        "collection": "my_docs"
    }
}

rag = KaliRAG(**config)

# Create and store embeddings
text = "Your long document text here..."
result = rag.create_store_embedding(text)

# Retrieve relevant chunks
response = rag.retrieve_embedding("What is the main topic?", top_k=3)
print(response)
```

### Method 2: Configure Separately (Recommended)

```python
from ragify import KaliRAG

# Initialize with defaults
rag = KaliRAG()

# Configure database with separate parameters
rag.configure_database(
    api_key="your-quadrant-api-key",
    host="https://api.quadrant.io",
    port=443,  # Optional
    collection="my_docs"
)

# Configure embedding model
rag.configure_embedding_model("sentence-transformers/all-MiniLM-L6-v2")

# Configure chunking parameters
rag.configure_chunking(chunk_size=512, chunk_overlap=50)

# Now use the configured RAG system
result = rag.create_store_embedding("Your text here...")
```

## 📦 Installation

```bash
pip install ragify
```

Or install from source:

```bash
git clone https://github.com/ragify/ragify.git
cd ragify
pip install -e .
```

## 🎯 Features

### ✅ Core Features

- **Simple API**: Two main functions - `create_store_embedding()` and `retrieve_embedding()`
- **Smart Chunking**: Automatic text chunking with configurable size and overlap
- **Multiple Embedding Models**: Support for HuggingFace SentenceTransformers
- **Vector Database Integration**: Native support for Quadrant (with mock mode for testing)
- **Configurable**: Easy customization of chunking, embedding, and retrieval parameters

### 🔧 Advanced Features

- **Recursive Chunking**: Automatically handles very long documents
- **Similarity Thresholds**: Filter results by similarity score
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling with detailed error messages
- **Mock Mode**: Works without external dependencies for testing

## 📚 Usage Examples

### Basic Usage

```python
from ragify import KaliRAG

# Initialize with defaults
rag = KaliRAG()

# Add your documents
text = """
RAG stands for Retrieval-Augmented Generation. It's a technique that combines 
large language models with external knowledge retrieval to provide more accurate 
and contextually relevant responses.
"""

# Create embeddings and store them
result = rag.create_store_embedding(text)
print(f"Created {result['chunks_created']} chunks")

# Query your knowledge base
response = rag.retrieve_embedding("What is RAG?", top_k=3)
for result in response['results']:
    print(f"Score: {result['similarity_score']:.3f}")
    print(f"Text: {result['text']}")
```

### Advanced Configuration

```python
# Custom configuration
config = {
    "embedding_model": "sentence-transformers/all-mpnet-base-v2",
    "chunk_size": 256,
    "chunk_overlap": 25,
    "db_config": {
        "api_key": "your-api-key",
        "collection": "custom_collection"
    }
}

rag = KaliRAG(**config)

# Use recursive chunking for very long documents
long_text = "..." * 1000  # Very long text
result = rag.create_store_embedding(
    long_text,
    use_recursive_chunking=True,
    max_recursion_depth=3
)

# Retrieve with custom parameters
response = rag.retrieve_embedding(
    "Your query",
    top_k=5,
    similarity_threshold=0.8
)
```

### System Information

```python
# Get system configuration
info = rag.get_info()
print(f"Embedding model: {info['embedding_model']}")
print(f"Embedding dimension: {info['embedding_dimension']}")
print(f"Chunk size: {info['chunk_size']}")
```

## 🏗️ Architecture

Ragify is built with a modular architecture:

```
ragify/
├── core/
│   ├── ragify.py          # Main KaliRAG class
│   ├── chunker.py         # Text chunking logic
│   ├── embedder.py        # Embedding model management
│   └── db_quadrant.py     # Vector database integration
├── utils/
│   └── logger.py          # Logging utilities
├── config/
│   └── defaults.py        # Default configurations
└── examples/
    └── basic_usage.py     # Usage examples
```

## 🔧 Configuration

### Embedding Models

Supported models (via HuggingFace SentenceTransformers):

- `sentence-transformers/all-MiniLM-L6-v2` (default)
- `sentence-transformers/all-mpnet-base-v2`
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Chunking Parameters

- `chunk_size`: Maximum size of each chunk (default: 512)
- `chunk_overlap`: Overlap between consecutive chunks (default: 50)

### Retrieval Parameters

- `top_k`: Number of top results to return (default: 3)
- `similarity_threshold`: Minimum similarity score (default: 0.7)

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run with coverage:

```bash
python -m pytest tests/ --cov=ragify
```

## 🖥️ Command Line Interface

Ragify includes a CLI for easy configuration and usage:

### Configure Settings

```bash
# Configure database
ragify config --api-key "your-key" --host "https://api.quadrant.io" --collection "my_docs"

# Configure with port
ragify config --api-key "your-key" --host "https://api.quadrant.io" --port 443 --collection "my_docs"

# Configure embedding model
ragify config --model "sentence-transformers/all-mpnet-base-v2"

# Configure chunking
ragify config --chunk-size 256 --chunk-overlap 25

# Configure everything at once
ragify config --api-key "your-key" --model "all-MiniLM-L6-v2" --chunk-size 512
```

### Get System Information

```bash
ragify info
```

### Create Embeddings from File

```bash
ragify create --input document.txt --output results.json
```

### Query the Knowledge Base

```bash
ragify query "What is RAG?" --top-k 5 --threshold 0.8
```

### Reset Database

```bash
ragify reset
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/ragify/ragify.git
cd ragify
pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [HuggingFace](https://huggingface.co/) for the excellent SentenceTransformers library
- [Quadrant](https://quadrant.io/) for the vector database integration
- The open-source AI community for inspiration and feedback

## 📞 Support

- 📧 Email: team@ragify.com
- 🐛 Issues: [GitHub Issues](https://github.com/ragify/ragify/issues)
- 📖 Documentation: [Read the Docs](https://ragify.readthedocs.io/)

## 🚀 Roadmap

- [ ] OpenAI embedding support
- [ ] Additional vector databases (Chroma, FAISS, Pinecone)
- [ ] File loaders (PDF, CSV, DOCX)
- [ ] CLI interface
- [ ] Web UI
- [ ] FastAPI wrapper
- [ ] Batch processing
- [ ] Advanced chunking strategies

---

**Made with ❤️ by the Ragify Team** 