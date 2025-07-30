"""
Command-line interface for Ragify
"""

import argparse
import json
import sys
from typing import Dict, Any
from . import KaliRAG


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Ragify - A simple RAG library for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize and get system info
  ragify info

  # Create embeddings from text file
  ragify create --input document.txt --output embeddings.json

  # Query the knowledge base
  ragify query "What is RAG?" --top-k 5

  # Full workflow example
  ragify create --input data.txt && ragify query "Your question here"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get system information")
    info_parser.add_argument("--config", help="Configuration file path")
    
    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure RAG settings")
    config_parser.add_argument("--api-key", help="Quadrant API key")
    config_parser.add_argument("--host", help="Quadrant host URL")
    config_parser.add_argument("--port", type=int, help="Quadrant port number")
    config_parser.add_argument("--collection", help="Collection name")
    config_parser.add_argument("--model", help="Embedding model name")
    config_parser.add_argument("--chunk-size", type=int, help="Chunk size")
    config_parser.add_argument("--chunk-overlap", type=int, help="Chunk overlap")
    config_parser.add_argument("--config-file", help="Configuration file path")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create and store embeddings")
    create_parser.add_argument("--input", "-i", required=True, help="Input text file")
    create_parser.add_argument("--output", "-o", help="Output file for results")
    create_parser.add_argument("--config", help="Configuration file path")
    create_parser.add_argument("--recursive", action="store_true", help="Use recursive chunking")
    create_parser.add_argument("--max-depth", type=int, default=3, help="Max recursion depth")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the knowledge base")
    query_parser.add_argument("query", help="Query string")
    query_parser.add_argument("--top-k", type=int, default=3, help="Number of top results")
    query_parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold")
    query_parser.add_argument("--config", help="Configuration file path")
    query_parser.add_argument("--output", "-o", help="Output file for results")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset the database")
    reset_parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Load configuration
        config = load_config(args.config) if args.config else {}
        
        # Initialize RAG
        rag = KaliRAG(**config)
        
        if args.command == "info":
            handle_info(rag, args)
        elif args.command == "config":
            handle_config(rag, args)
        elif args.command == "create":
            handle_create(rag, args)
        elif args.command == "query":
            handle_query(rag, args)
        elif args.command == "reset":
            handle_reset(rag, args)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config file {config_path}: {str(e)}")


def save_output(data: Dict[str, Any], output_path: str):
    """
    Save output to file
    
    Args:
        data: Data to save
        output_path: Output file path
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Warning: Failed to save to {output_path}: {str(e)}")


def handle_info(rag: KaliRAG, args):
    """
    Handle info command
    
    Args:
        rag: KaliRAG instance
        args: Command line arguments
    """
    info = rag.get_info()
    print("System Information:")
    print(json.dumps(info, indent=2))


def handle_config(rag: KaliRAG, args):
    """
    Handle config command
    
    Args:
        rag: KaliRAG instance
        args: Command line arguments
    """
    success = True
    
    # Configure database if database-related arguments are provided
    if any([args.api_key, args.host, args.port, args.collection]):
        if not args.api_key:
            print("Error: --api-key is required for database configuration", file=sys.stderr)
            sys.exit(1)
        
        db_success = rag.configure_database(
            api_key=args.api_key,
            host=args.host or "https://api.quadrant.io",
            port=args.port,
            collection=args.collection or "ragify_docs"
        )
        
        if db_success:
            print("✅ Database configured successfully")
        else:
            print("❌ Failed to configure database")
            success = False
    
    # Configure embedding model if specified
    if args.model:
        model_success = rag.configure_embedding_model(args.model)
        if model_success:
            print(f"✅ Embedding model configured: {args.model}")
        else:
            print(f"❌ Failed to configure embedding model: {args.model}")
            success = False
    
    # Configure chunking if specified
    if args.chunk_size or args.chunk_overlap:
        chunk_size = args.chunk_size or 512
        chunk_overlap = args.chunk_overlap or 50
        
        chunk_success = rag.configure_chunking(chunk_size, chunk_overlap)
        if chunk_success:
            print(f"✅ Chunking configured: size={chunk_size}, overlap={chunk_overlap}")
        else:
            print(f"❌ Failed to configure chunking")
            success = False
    
    # Load from config file if specified
    if args.config_file:
        try:
            config = load_config(args.config_file)
            
            # Apply database config if present
            if "db_config" in config:
                db_config = config["db_config"]
                db_success = rag.configure_database(
                    api_key=db_config.get("api_key", "mock_key"),
                    host=db_config.get("host", "https://api.quadrant.io"),
                    collection=db_config.get("collection", "ragify_docs")
                )
                if db_success:
                    print("✅ Database configured from file")
                else:
                    print("❌ Failed to configure database from file")
                    success = False
            
            # Apply other configs
            if "embedding_model" in config:
                model_success = rag.configure_embedding_model(config["embedding_model"])
                if model_success:
                    print(f"✅ Embedding model configured from file: {config['embedding_model']}")
                else:
                    print(f"❌ Failed to configure embedding model from file")
                    success = False
            
            if "chunk_size" in config or "chunk_overlap" in config:
                chunk_size = config.get("chunk_size", 512)
                chunk_overlap = config.get("chunk_overlap", 50)
                chunk_success = rag.configure_chunking(chunk_size, chunk_overlap)
                if chunk_success:
                    print(f"✅ Chunking configured from file: size={chunk_size}, overlap={chunk_overlap}")
                else:
                    print(f"❌ Failed to configure chunking from file")
                    success = False
                    
        except Exception as e:
            print(f"❌ Failed to load config file: {str(e)}", file=sys.stderr)
            success = False
    
    if success:
        print("\n🎉 Configuration completed successfully!")
        print("\nCurrent configuration:")
        info = rag.get_info()
        print(json.dumps(info, indent=2))
    else:
        print("\n⚠️  Some configurations failed. Check the errors above.")
        sys.exit(1)


def handle_create(rag: KaliRAG, args):
    """
    Handle create command
    
    Args:
        rag: KaliRAG instance
        args: Command line arguments
    """
    try:
        # Read input file
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Processing file: {args.input}")
        print(f"Text length: {len(text)} characters")
        
        # Create embeddings
        result = rag.create_store_embedding(
            text,
            use_recursive_chunking=args.recursive,
            max_recursion_depth=args.max_depth
        )
        
        if result["success"]:
            print(f"✅ Successfully created {result['chunks_created']} chunks")
            print(f"✅ Successfully stored {result['chunks_stored']} embeddings")
            
            if args.output:
                save_output(result, args.output)
        else:
            print(f"❌ Failed: {result['error']}")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_query(rag: KaliRAG, args):
    """
    Handle query command
    
    Args:
        rag: KaliRAG instance
        args: Command line arguments
    """
    print(f"Querying: {args.query}")
    
    result = rag.retrieve_embedding(
        args.query,
        top_k=args.top_k,
        similarity_threshold=args.threshold
    )
    
    if result["success"]:
        print(f"Found {result['total_results']} results:")
        print()
        
        for i, item in enumerate(result["results"], 1):
            print(f"{i}. Score: {item['similarity_score']:.3f}")
            print(f"   Text: {item['text'][:100]}...")
            print()
        
        if args.output:
            save_output(result, args.output)
    else:
        print(f"❌ Failed: {result['error']}")
        sys.exit(1)


def handle_reset(rag: KaliRAG, args):
    """
    Handle reset command
    
    Args:
        rag: KaliRAG instance
        args: Command line arguments
    """
    print("Resetting database...")
    
    result = rag.reset_database()
    
    if result["success"]:
        print("✅ Database reset successfully")
    else:
        print(f"❌ Failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main() 