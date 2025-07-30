#!/usr/bin/env python3
"""Test MCP server startup time."""

import time
import os
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

def test_startup_time():
    print("Testing MCP server initialization time...\n")
    
    # Set embedding server URL
    os.environ["THOTH_EMBEDDING_SERVER_URL"] = "http://localhost:8765"
    
    # Time the imports and initialization
    start_time = time.time()
    
    # Import the storage backend
    from thoth.storage.backend import ThothStorage
    
    # Create storage instance
    storage = ThothStorage(
        embedding_server_url="http://localhost:8765",
        use_vllm=True
    )
    
    create_time = time.time()
    print(f"✓ Storage instance created in {create_time - start_time:.2f}s")
    
    # Time the async initialization
    import asyncio
    
    async def init_storage():
        await storage.initialize()
    
    init_start = time.time()
    asyncio.run(init_storage())
    init_time = time.time()
    
    print(f"✓ Storage initialized in {init_time - init_start:.2f}s")
    print(f"✓ Total time: {init_time - start_time:.2f}s")
    
    # Check what embedder is being used
    print(f"\nUsing embedder: {storage.embedder.__class__.__name__}")
    
    # Check ChromaDB collection
    if storage.chroma_collection:
        count = storage.chroma_collection.count()
        print(f"ChromaDB has {count} embeddings already stored")

if __name__ == "__main__":
    test_startup_time()