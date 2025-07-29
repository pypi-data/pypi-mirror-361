"""Command-line interface for GRASS RAG Pipeline."""

import argparse
import asyncio
import time
import sys
from loguru import logger
from .pipeline import RAGPipeline
from . import __version__

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GRASS GIS RAG Pipeline - AI-powered GRASS command generation"
    )
    
    parser.add_argument("--question", "-q", type=str, required=True, help="GRASS GIS question to ask")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode")
    parser.add_argument("--async", action="store_true", dest="async_mode", help="Use async processing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--version", action="version", version=f"grass-rag-pipeline {__version__}")
    
    args = parser.parse_args()
    
    try:
        rag = RAGPipeline(offline=args.offline)
        
        if args.async_mode:
            response = asyncio.run(rag.aquery(args.question))
        else:
            response = rag.query(args.question)
        
        answer, results, metrics = response
        
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}")
        print(f"Time: {metrics['total_latency']:.3f}s")
        print(f"Quality: {metrics['f1_score']:.3f}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())