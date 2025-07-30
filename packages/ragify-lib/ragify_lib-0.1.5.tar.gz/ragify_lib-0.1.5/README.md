# ragify-lib: Effortless Retrieval-Augmented Generation (RAG) Workflows in Python

**ragify-lib** is a modern, production-ready Python library that makes Retrieval-Augmented Generation (RAG) simple, fast, and flexible. With just a few lines of code, you can chunk, embed, store, and retrieve text using state-of-the-art embedding models and vector databases. Whether you’re building chatbots, search engines, or knowledge assistants, ragify-lib helps you unlock the power of RAG with minimal setup.

---

## 🚀 Why Choose ragify-lib?

- **Minimal Setup**: Go from raw text to powerful retrieval in minutes.
- **Flexible**: Easily configure your embedding model, chunking strategy, and vector database (supports Quadrant and mock mode).
- **Human-Readable Results**: Retrieve relevant text chunks with similarity scores and metadata—no need to handle raw embeddings.
- **CLI Included**: Use the command-line tool for quick experiments and automation.
- **Open Source**: Free to use for research and commercial projects.

---

## 👤 About the Developer

**Rahul Wale**  
AI Developer & Researcher  
Rahul specializes in building practical, scalable AI solutions for real-world problems, with a focus on natural language processing and information retrieval.

---

## 📦 Installation

```bash
pip install ragify-lib
```

---

## 📝 Example 1: Local RAG Workflow in Python

```python
from ragify import KaliRAG

# 1. Configure your database and embedding model (optional, uses sensible defaults)
rag = KaliRAG()
rag.configure_database(api_key="mock_key", host="localhost", port=6333, collection="my_collection")
rag.configure_embedding_model("all-MiniLM-L6-v2")
rag.configure_chunking(chunk_size=256, chunk_overlap=32)

# 2. Store your documents
documents = [
    "Retrieval-Augmented Generation (RAG) combines retrieval and generation for better answers.",
    "ragify-lib makes it easy to build RAG pipelines in Python.",
    "You can use Quadrant or mock mode for vector storage."
]
for doc in documents:
    rag.create_store_embedding(doc)

# 3. Retrieve relevant chunks for a query
results = rag.retrieve_embedding("How does RAG work?")
for chunk in results["results"]:
    print(f"Text: {chunk['text']}\nScore: {chunk['score']}\n")
```

---

## 📝 Example 2: File-Based Workflow & CLI Usage

**Create embeddings from a file and query them using the CLI:**

```bash
# Store embeddings from a text file
ragify create --input knowledge.txt --output embeddings.json --api-key mock_key

# Query your knowledge base
ragify query "What is retrieval-augmented generation?" --top-k 3
```

**Or configure everything via the CLI:**

```bash
ragify config --api-key mock_key --host "localhost" --port 6333 --collection "my_collection" --model "all-MiniLM-L6-v2" --chunk-size 256 --chunk-overlap 32
```

> **Note:** Use `--api-key mock_key` for local/mock mode. For production, use your real Quadrant API key.

---

## 🌟 Features

- **Plug-and-play** with Quadrant vector database or use built-in mock mode
- **Customizable chunking and embedding** for any use case
- **Returns human-readable results** with scores and metadata
- **Designed for both developers and researchers**
- **Robust CLI** for automation and scripting
- **Easy integration** with existing Python projects

---

## 🛠️ Advanced Usage

- **Recursive Chunking**: Handles very long documents with automatic recursion.
- **Similarity Thresholds**: Filter results by similarity score.
- **Comprehensive Logging**: Built-in logging for debugging and monitoring.
- **Error Handling**: Robust error handling with detailed error messages.

---

## 📚 Use Cases

- AI-powered chatbots and assistants
- Semantic search engines
- Knowledge base augmentation
- Research and prototyping in NLP

---

## 📖 Documentation

For full documentation, visit the [official docs](https://ragify.readthedocs.io/) or see the CLI help:

```bash
ragify --help
```

---

## 📄 License

This project is licensed under the MIT License.

---

**ragify-lib**: The easiest way to add Retrieval-Augmented Generation to your Python projects. 