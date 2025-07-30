"""
Unified storage backend with semantic search capabilities.
Supports vLLM embeddings with ChromaDB vector storage.
"""

import json
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import networkx as nx
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import Database
from .models import Repository, File, Symbol, Import, Call
from ..embeddings import EmbeddingProvider, TfidfEmbedder
from ..embeddings.remote_embedder import RemoteEmbedder

logger = logging.getLogger(__name__)


class ThothStorage:
    """
    Unified storage backend with semantic search.
    
    Components:
    - SQLite: Source of truth for all structured data
    - ChromaDB: Vector storage for semantic search
    - NetworkX: In-memory graph for relationships
    - Embeddings: vLLM (primary) or TF-IDF (fallback)
    - Redis: Optional caching layer
    """
    
    def __init__(
        self,
        db_path: str = "~/.thoth/index.db",
        use_vllm: bool = True,
        vllm_model: str = "Qwen/Qwen3-Embedding-0.6B",
        use_redis: bool = False,
        redis_url: str = "redis://localhost:6379",
        embedding_server_url: Optional[str] = None,
        chromadb_server_url: Optional[str] = None
    ):
        """Initialize storage backend.
        
        Args:
            db_path: Path to SQLite database
            use_vllm: Whether to use vLLM for embeddings
            vllm_model: vLLM model to use
            use_redis: Whether to enable Redis caching
            redis_url: Redis connection URL
            embedding_server_url: URL of external embedding server (e.g. http://localhost:8765)
            chromadb_server_url: URL of external ChromaDB server (e.g. http://localhost:8000)
        """
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.db = Database(str(self.db_path))
        self.graph = None  # Lazy load when needed
        self._graph_loaded = False
        
        # Use remote embedder if server URL provided, otherwise TF-IDF fallback
        if embedding_server_url and use_vllm:
            self.embedder = RemoteEmbedder(
                base_url=embedding_server_url,
                model_name="qwen3"  # Indicate we're using Qwen3 for proper instruction formatting
            )
            logger.info(f"Using remote embedding server at {embedding_server_url}")
        else:
            # Fallback to TF-IDF if no remote server
            self.embedder = TfidfEmbedder()
            logger.info("Using TF-IDF embedder (no remote embedding server configured)")
        
        # Optional Redis cache
        self.redis = None
        if use_redis:
            try:
                import redis
                self.redis = redis.from_url(redis_url)
                self.redis.ping()
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        
        # ChromaDB will be initialized after embedder is ready
        self.chroma = None
        self.chroma_collection = None
        self.chromadb_server_url = chromadb_server_url
    
    def _init_chromadb(self) -> None:
        """Initialize ChromaDB for vector storage."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Always use ChromaDB server
            chromadb_url = self.chromadb_server_url or os.getenv("THOTH_CHROMADB_SERVER_URL", "http://localhost:8000")
            
            # Parse URL to get host and port
            import urllib.parse
            parsed = urllib.parse.urlparse(chromadb_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 8000
            
            try:
                self.chroma = chromadb.HttpClient(
                    host=host,
                    port=port,
                    settings=Settings(
                        anonymized_telemetry=False
                    )
                )
                logger.info(f"Connected to ChromaDB server at {host}:{port}")
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB server at {host}:{port}")
                logger.error("Please ensure ChromaDB server is running:")
                logger.error("  Run: ./scripts/run_chromadb_server.sh")
                raise RuntimeError(f"ChromaDB server connection failed: {e}")
            
            # Get or create collection
            try:
                # Try to get existing collection
                self.chroma_collection = self.chroma.get_collection(name="thoth_symbols")
                logger.info("Using existing ChromaDB collection")
            except Exception:
                # Collection doesn't exist, create it
                self.chroma_collection = self.chroma.create_collection(
                    name="thoth_symbols",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Created new ChromaDB collection")
            
            logger.info("ChromaDB initialized for vector storage")
            
        except ImportError:
            logger.error("ChromaDB not installed. Install with: pip install chromadb>=0.4.0")
            raise
    
    def _get_embedding_dim(self) -> int:
        """Get the dimension of embeddings from the current embedder."""
        # Test with a dummy text to get dimension
        test_embedding = self.embedder.encode("test")
        if hasattr(test_embedding, 'shape'):
            return test_embedding.shape[-1]
        return len(test_embedding)
    
    async def initialize(self) -> None:
        """Initialize all storage components."""
        await self.db.init_db()
        self._init_chromadb()  # Initialize ChromaDB after embedder is ready
        # Don't load graph on startup - load lazily when needed
        # await self._load_graph()
        # Don't load embeddings on startup - they're already in ChromaDB from indexing
        # await self._load_embeddings()
    
    async def _ensure_graph_loaded(self) -> None:
        """Ensure graph is loaded (lazy loading)."""
        if self._graph_loaded:
            return
        
        if self.graph is None:
            self.graph = nx.DiGraph()
        
        await self._load_graph()
        self._graph_loaded = True
    
    async def _load_graph(self) -> None:
        """Load graph structure from database."""
        import time
        start_time = time.time()
        async with self.db.get_session() as session:
            # Load all symbols as nodes
            result = await session.execute(
                select(Symbol).options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbols = result.scalars().all()
            
            for symbol in symbols:
                self.graph.add_node(
                    f"symbol_{symbol.id}",
                    name=symbol.name,
                    type=symbol.type,
                    repo=symbol.repository.name,
                    file_path=symbol.file.path,
                    line=symbol.line,
                    docstring=symbol.docstring
                )
            
            # Load call relationships
            result = await session.execute(select(Call))
            calls = result.scalars().all()
            
            for call in calls:
                if call.caller_symbol_id and call.callee_symbol_id:
                    self.graph.add_edge(
                        f"symbol_{call.caller_symbol_id}",
                        f"symbol_{call.callee_symbol_id}",
                        type="calls"
                    )
            
            # Load import relationships (file to file)
            result = await session.execute(select(Import))
            imports = result.scalars().all()
            
            for imp in imports:
                if imp.resolved_file_id:
                    self.graph.add_edge(
                        f"file_{imp.file_id}",
                        f"file_{imp.resolved_file_id}",
                        type="imports"
                    )
            
            load_time = time.time() - start_time
            logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges in {load_time:.2f}s")
    
    async def _compute_all_embeddings(self) -> None:
        """Compute embeddings for all symbols and store in ChromaDB.
        
        This should only be called during indexing, not on MCP server startup.
        """
        async with self.db.get_session() as session:
            result = await session.execute(
                select(Symbol).options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbols = result.scalars().all()
            
            if not symbols:
                logger.info("No symbols to embed")
                return
            
            # Prepare texts for embedding
            texts = []
            metadatas = []
            ids = []
            
            for symbol in symbols:
                # Create rich text representation for embedding
                text_parts = [
                    f"{symbol.type} {symbol.name}",
                    f"in {symbol.repository.name}/{symbol.file.path}",
                ]
                if symbol.docstring:
                    text_parts.append(f"docstring: {symbol.docstring}")
                
                text = " ".join(text_parts)
                texts.append(text)
                
                # Metadata for ChromaDB
                metadatas.append({
                    "symbol_id": symbol.id,
                    "name": symbol.name,
                    "type": symbol.type,
                    "repo": symbol.repository.name,
                    "file_path": symbol.file.path,
                    "line": symbol.line
                })
                
                ids.append(f"symbol_{symbol.id}")
            
            # Fit TF-IDF if using it
            if hasattr(self.embedder, 'fit'):
                logger.info("Fitting embedder on symbol texts")
                self.embedder.fit(texts)
            
            # Compute embeddings in batches
            batch_size = 32  # TEI ONNX max batch size
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                # Get embeddings (handle both sync and async embedders)
                if hasattr(self.embedder, 'encode_async'):
                    embeddings = await self.embedder.encode_async(batch_texts)
                else:
                    embeddings = self.embedder.encode(batch_texts)
                if not isinstance(embeddings, list):
                    embeddings = [embeddings]
                
                # Convert to CPU numpy arrays to free GPU memory
                cpu_embeddings = []
                for emb in embeddings:
                    if hasattr(emb, 'cpu'):
                        # If it's a torch tensor, move to CPU
                        cpu_embeddings.append(emb.cpu().numpy())
                    else:
                        # Already numpy array
                        cpu_embeddings.append(emb)
                
                # Store in ChromaDB
                self.chroma_collection.upsert(
                    embeddings=[emb.tolist() for emb in cpu_embeddings],
                    documents=batch_texts,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                
                logger.info(f"Embedded batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            logger.info(f"Completed embedding {len(texts)} symbols")
    
    async def search_semantic(
        self,
        query: str,
        repo: Optional[str] = None,
        symbol_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Semantic search for symbols.
        
        Args:
            query: Search query
            repo: Filter by repository name
            symbol_type: Filter by symbol type (function, class, method)
            limit: Maximum results to return
            
        Returns:
            List of matching symbols with scores
        """
        if not self.chroma_collection:
            raise RuntimeError("ChromaDB not initialized")
        
        # Build filter
        where = {}
        if repo:
            where["repo"] = repo
        if symbol_type:
            where["type"] = symbol_type
        
        # Encode query with same embedder used for indexing
        if hasattr(self.embedder, 'encode_async'):
            query_embedding = await self.embedder.encode_async(query)
        else:
            query_embedding = self.embedder.encode(query)
        if hasattr(query_embedding, 'cpu'):
            query_embedding = query_embedding.cpu().numpy()
        
        # Search ChromaDB with embedding
        results = self.chroma_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit,
            where=where if where else None
        )
        
        # Format results
        output = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                score = 1.0 - (results['distances'][0][i] if results['distances'] else 0.5)
                
                output.append({
                    "symbol_id": metadata["symbol_id"],
                    "name": metadata["name"],
                    "type": metadata["type"],
                    "repo": metadata["repo"],
                    "file_path": metadata["file_path"],
                    "line": metadata["line"],
                    "score": score,
                    "preview": results['documents'][0][i][:200] + "..."
                })
        
        return output
    
    async def get_symbol_context(
        self,
        symbol_id: int,
        include_callers: bool = True,
        include_callees: bool = True,
        depth: int = 1
    ) -> Dict[str, Any]:
        """Get rich context for a symbol including relationships.
        
        Args:
            symbol_id: Symbol ID to get context for
            include_callers: Include functions that call this symbol
            include_callees: Include functions called by this symbol
            depth: How many levels deep to traverse
            
        Returns:
            Symbol context with relationships
        """
        async with self.db.get_session() as session:
            # Get symbol details
            result = await session.execute(
                select(Symbol)
                .where(Symbol.id == symbol_id)
                .options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbol = result.scalar_one_or_none()
            
            if not symbol:
                return {}
            
            context = {
                "id": symbol.id,
                "name": symbol.name,
                "type": symbol.type,
                "file_path": symbol.file.path,
                "line": symbol.line,
                "docstring": symbol.docstring,
                "repository": symbol.repository.name
            }
            
            node_id = f"symbol_{symbol_id}"
            
            # Get relationships from graph
            if include_callers and node_id in self.graph:
                callers = []
                for pred in self.graph.predecessors(node_id):
                    if self.graph.edges[pred, node_id].get('type') == 'calls':
                        callers.append(self.graph.nodes[pred])
                context["called_by"] = callers
            
            if include_callees and node_id in self.graph:
                callees = []
                for succ in self.graph.successors(node_id):
                    if self.graph.edges[node_id, succ].get('type') == 'calls':
                        callees.append(self.graph.nodes[succ])
                context["calls"] = callees
            
            return context
    
    async def update_symbol_embeddings(
        self,
        symbol_ids: Optional[List[int]] = None
    ) -> None:
        """Update embeddings for specific symbols or all symbols.
        
        Args:
            symbol_ids: List of symbol IDs to update, or None for all
        """
        async with self.db.get_session() as session:
            query = select(Symbol).options(
                selectinload(Symbol.repository),
                selectinload(Symbol.file)
            )
            
            if symbol_ids:
                query = query.where(Symbol.id.in_(symbol_ids))
            
            result = await session.execute(query)
            symbols = result.scalars().all()
            
            # Update embeddings
            for symbol in symbols:
                text = f"{symbol.type} {symbol.name} in {symbol.repository.name}/{symbol.file.path}"
                if symbol.docstring:
                    text += f" docstring: {symbol.docstring}"
                
                if hasattr(self.embedder, 'encode_async'):
                    embedding = await self.embedder.encode_async(text)
                else:
                    embedding = self.embedder.encode(text)
                if isinstance(embedding, list):
                    embedding = embedding[0]
                
                # Update in ChromaDB
                self.chroma_collection.update(
                    embeddings=[embedding.tolist()],
                    documents=[text],
                    metadatas=[{
                        "symbol_id": symbol.id,
                        "name": symbol.name,
                        "type": symbol.type,
                        "repo": symbol.repository.name,
                        "file_path": symbol.file.path,
                        "line": symbol.line
                    }],
                    ids=[f"symbol_{symbol.id}"]
                )
        
        logger.info(f"Updated embeddings for {len(symbols)} symbols")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with storage stats
        """
        # Ensure graph is loaded for accurate stats
        await self._ensure_graph_loaded()
        
        stats = {
            "total_symbols": len([n for n in self.graph.nodes if n.startswith("symbol_")]),
            "total_files": len([n for n in self.graph.nodes if n.startswith("file_")]),
            "total_calls": len([e for e in self.graph.edges if self.graph.edges[e].get('type') == 'calls']),
            "total_imports": len([e for e in self.graph.edges if self.graph.edges[e].get('type') == 'imports']),
            "embedding_type": self.embedder.embedder_type if hasattr(self.embedder, 'embedder_type') else type(self.embedder).__name__,
            "redis_enabled": self.redis is not None,
            "chromadb_enabled": self.chroma is not None
        }
        
        if self.chroma_collection:
            stats["vector_count"] = self.chroma_collection.count()
        
        # Get repository list
        repos = set()
        for node, data in self.graph.nodes(data=True):
            if 'repo' in data:
                repos.add(data['repo'])
        stats["repositories"] = sorted(list(repos))
        
        return stats
    
    async def get_changed_files(self, repo_id: int) -> List[int]:
        """Get files that have changed since last indexing.
        
        Args:
            repo_id: Repository ID to check
            
        Returns:
            List of file IDs that need re-indexing
        """
        changed_files = []
        
        async with self.db.get_session() as session:
            result = await session.execute(
                select(File).where(File.repository_id == repo_id)
            )
            files = result.scalars().all()
            
            for file in files:
                file_path = Path(file.path)
                if file_path.exists():
                    # Check if file has been modified
                    current_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file.last_modified is None or current_mtime > file.last_modified:
                        # Also check content hash for real changes
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        current_hash = hashlib.sha256(content.encode()).hexdigest()
                        
                        if file.content_hash != current_hash:
                            changed_files.append(file.id)
        
        return changed_files
    
    async def close(self) -> None:
        """Cleanup resources."""
        if self.redis:
            self.redis.close()
        
        logger.info("Storage backend closed")