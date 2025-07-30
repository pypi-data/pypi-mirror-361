"""Remote embedding client for connecting to external embedding services."""

from typing import Union, List, Optional
import numpy as np
import httpx
import logging
from urllib.parse import urljoin
import asyncio

logger = logging.getLogger(__name__)


class RemoteEmbedder:
    """Client for remote embedding services (vLLM server, TEI, etc.)."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model_name: Optional[str] = None,
        timeout: float = 30.0,
        api_key: Optional[str] = None
    ):
        """Initialize remote embedder client.
        
        Args:
            base_url: Base URL of embedding service
            model_name: Model name (for OpenAI-compatible endpoints)
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self.headers
        )
        
        # Detect API type (TEI vs OpenAI)
        self.api_type = self._detect_api_type()
        
        # Check if service is available
        self._check_service()
    
    def _detect_api_type(self) -> str:
        """Detect if the server is TEI or OpenAI-compatible."""
        try:
            # Try TEI health endpoint
            response = httpx.get(
                urljoin(self.base_url, "/health"),
                timeout=5.0
            )
            if response.status_code == 200:
                return "tei"
        except:
            pass
        
        # Default to OpenAI
        return "openai"
    
    def _check_service(self) -> None:
        """Check if remote service is available."""
        try:
            # Try sync request for initialization
            response = httpx.get(
                urljoin(self.base_url, "/health"),
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info(f"Connected to embedding service at {self.base_url}")
            else:
                logger.warning(f"Embedding service returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to embedding service: {e}")
    
    async def _embed_async(self, texts: List[str]) -> List[np.ndarray]:
        """Async embedding request."""
        try:
            if self.api_type == "tei":
                # TEI endpoint - add instruction prefix for Qwen3
                # Check if we're using Qwen3 model
                if self.model_name and "qwen3" in self.model_name.lower():
                    # Add instruction prefix for code embeddings
                    instructed_texts = []
                    for text in texts:
                        instructed = f"Instruct: Represent this code for retrieval\nQuery: {text}"
                        instructed_texts.append(instructed)
                    texts = instructed_texts
                
                payload = {"inputs": texts}
                response = await self.client.post(
                    urljoin(self.base_url, "/embed"),
                    json=payload
                )
                response.raise_for_status()
                
                # TEI returns embeddings directly as array
                data = response.json()
                embeddings = [np.array(emb, dtype=np.float32) for emb in data]
                
            else:
                # OpenAI-compatible endpoint
                payload = {
                    "input": texts,
                    "model": self.model_name or "default"
                }
                
                response = await self.client.post(
                    urljoin(self.base_url, "/v1/embeddings"),
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                embeddings = []
                
                # Extract embeddings from OpenAI format
                for item in data["data"]:
                    embedding = np.array(item["embedding"])
                    embeddings.append(embedding)
            
            return embeddings
            
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to embedding service")
            raise
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise
    
    def encode(
        self,
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode text using remote service.
        
        Args:
            text: Single text or list of texts
            
        Returns:
            Single embedding array or list of arrays
        """
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
        
        try:
            # Use synchronous HTTP client for sync context
            if self.api_type == "tei":
                # TEI endpoint - add instruction prefix for Qwen3
                # Check if we're using Qwen3 model
                if self.model_name and "qwen3" in self.model_name.lower():
                    # Add instruction prefix for code embeddings
                    instructed_texts = []
                    for text in texts:
                        instructed = f"Instruct: Represent this code for retrieval\nQuery: {text}"
                        instructed_texts.append(instructed)
                    texts = instructed_texts
                
                response = httpx.post(
                    urljoin(self.base_url, "/embed"),
                    json={"inputs": texts},
                    timeout=self.timeout,
                    headers=self.headers
                )
                response.raise_for_status()
                
                # TEI returns embeddings directly
                data = response.json()
                embeddings = [np.array(emb, dtype=np.float32) for emb in data]
                
            else:
                # OpenAI-compatible endpoint
                response = httpx.post(
                    urljoin(self.base_url, "/v1/embeddings"),
                    json={
                        "input": texts,
                        "model": self.model_name or "default"
                    },
                    timeout=self.timeout,
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                embeddings = []
                
                # Extract embeddings from OpenAI format
                for item in data["data"]:
                    embedding = np.array(item["embedding"])
                    embeddings.append(embedding)
            
            return embeddings[0] if single else embeddings
            
        except Exception as e:
            logger.error(f"Failed to get embeddings: {e}")
            # Return zero vectors as fallback
            dim = 1024  # Default dimension
            embeddings = [np.zeros(dim) for _ in texts]
            return embeddings[0] if single else embeddings
    
    async def encode_async(
        self,
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Async version of encode for use in async contexts.
        
        Args:
            text: Single text or list of texts
            
        Returns:
            Single embedding array or list of arrays
        """
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
        
        embeddings = await self._embed_async(texts)
        return embeddings[0] if single else embeddings
    
    def __del__(self):
        """Cleanup client."""
        # Async client will be cleaned up by garbage collector
        pass


class HybridEmbedder:
    """Hybrid embedder that tries remote first, falls back to local."""
    
    def __init__(
        self,
        remote_url: Optional[str] = None,
        fallback_embedder: Optional[object] = None
    ):
        """Initialize hybrid embedder.
        
        Args:
            remote_url: URL of remote embedding service
            fallback_embedder: Local embedder to use as fallback
        """
        self.remote_embedder = None
        self.fallback_embedder = fallback_embedder
        
        if remote_url:
            try:
                self.remote_embedder = RemoteEmbedder(remote_url)
                logger.info("Using remote embedding service")
            except Exception as e:
                logger.warning(f"Could not connect to remote service: {e}")
        
        if not self.remote_embedder and not self.fallback_embedder:
            # Create TF-IDF fallback
            from .tfidf import TfidfEmbedder
            self.fallback_embedder = TfidfEmbedder()
            logger.info("Using TF-IDF fallback embedder")
    
    def encode(
        self,
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode using remote service or fallback."""
        if self.remote_embedder:
            try:
                return self.remote_embedder.encode(text)
            except Exception as e:
                logger.warning(f"Remote embedding failed: {e}")
        
        if self.fallback_embedder:
            return self.fallback_embedder.encode(text)
        
        raise RuntimeError("No embedding service available")