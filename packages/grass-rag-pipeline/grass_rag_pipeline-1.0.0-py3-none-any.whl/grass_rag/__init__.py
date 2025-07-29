"""
GRASS GIS RAG Pipeline - High-performance chatbot for GRASS GIS commands

Example usage:
    >>> from grass_rag import GrassRAG
    >>> rag = GrassRAG()
    >>> answer, results, metrics = rag.query("How do I import shapefile?")
    >>> print(answer)
    `v.in.ogr input=file.shp output=vector_map`
"""

__version__ = "1.0.0"
__author__ = "Sachin NK"

# Main exports
from .pipeline import RAGPipeline as GrassRAG
from .pipeline import RAGPipeline
from .embedding import EmbeddingModel
from .model import QwenLLM

__all__ = [
    "GrassRAG",
    "RAGPipeline", 
    "EmbeddingModel",
    "QwenLLM",
    "__version__",
]