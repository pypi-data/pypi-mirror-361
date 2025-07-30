"""
Default configuration values for Ragify
"""

# Default embedding model
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50

# Default retrieval parameters
DEFAULT_TOP_K = 3
DEFAULT_SIMILARITY_THRESHOLD = 0.7

# Default Quadrant configuration
DEFAULT_QUADRANT_HOST = "https://api.quadrant.io"
DEFAULT_QUADRANT_COLLECTION = "ragify_docs"

# Supported embedding models
SUPPORTED_EMBEDDING_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
]

# Supported vector databases
SUPPORTED_VECTOR_DBS = ["quadrant"] 