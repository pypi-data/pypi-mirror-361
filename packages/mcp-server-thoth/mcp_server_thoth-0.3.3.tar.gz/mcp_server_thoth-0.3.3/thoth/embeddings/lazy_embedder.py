"""Lazy loading embedding wrapper that initializes on first use."""

from typing import Union, List, Optional
import numpy as np
import logging

from .base import EmbeddingProvider
from .tfidf import TfidfEmbedder
from .vllm_embedder import VLLMEmbedder

logger = logging.getLogger(__name__)


class LazyEmbedder:
    """Embedding provider that lazy loads the actual embedder on first use.
    
    This allows the MCP server to start quickly without waiting for
    heavy model initialization.
    """
    
    def __init__(
        self,
        use_vllm: bool = True,
        vllm_model: str = "Qwen/Qwen3-Embedding-0.6B",
        **kwargs
    ):
        """Initialize lazy embedder.
        
        Args:
            use_vllm: Whether to use vLLM (True) or TF-IDF (False)
            vllm_model: Model name for vLLM
            **kwargs: Additional arguments for the embedder
        """
        self.use_vllm = use_vllm
        self.vllm_model = vllm_model
        self.kwargs = kwargs
        self._embedder: Optional[EmbeddingProvider] = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize the actual embedder on first use."""
        if self._initialized:
            return
            
        logger.info("Initializing embedding provider (lazy load)...")
        
        if self.use_vllm:
            try:
                self._embedder = VLLMEmbedder(
                    model_name=self.vllm_model,
                    **self.kwargs
                )
                logger.info(f"Successfully loaded vLLM with {self.vllm_model}")
            except Exception as e:
                logger.warning(f"Failed to load vLLM: {e}. Falling back to TF-IDF")
                self._embedder = TfidfEmbedder()
        else:
            self._embedder = TfidfEmbedder()
            logger.info("Using TF-IDF embeddings")
        
        self._initialized = True
    
    def encode(
        self, 
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode text to embeddings, initializing embedder if needed.
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Single embedding array or list of embedding arrays
        """
        self._ensure_initialized()
        return self._embedder.encode(text)
    
    def fit(self, documents: List[str]) -> None:
        """Fit embedder on documents (only for TF-IDF).
        
        Args:
            documents: List of text documents to fit on
        """
        self._ensure_initialized()
        if hasattr(self._embedder, 'fit'):
            self._embedder.fit(documents)
    
    @property
    def embedder_type(self) -> str:
        """Get the type of embedder being used."""
        if not self._initialized:
            return "LazyEmbedder (not initialized)"
        return type(self._embedder).__name__