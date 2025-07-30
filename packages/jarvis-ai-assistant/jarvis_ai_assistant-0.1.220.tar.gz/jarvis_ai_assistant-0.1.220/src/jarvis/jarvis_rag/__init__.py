"""
Jarvis RAG Framework

A flexible RAG pipeline with pluggable remote LLMs and local, cache-enabled embedding models.
"""

from .rag_pipeline import JarvisRAGPipeline
from .llm_interface import LLMInterface
from .embedding_manager import EmbeddingManager

__all__ = ["JarvisRAGPipeline", "LLMInterface", "EmbeddingManager"]
