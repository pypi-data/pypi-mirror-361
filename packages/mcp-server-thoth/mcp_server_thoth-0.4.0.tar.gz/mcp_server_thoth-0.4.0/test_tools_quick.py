#!/usr/bin/env python3
"""Quick test of critical MCP tools."""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_tools():
    print("Testing MCP tools with external services...\n")
    
    # Set environment
    os.environ["THOTH_EMBEDDING_SERVER_URL"] = "http://localhost:8765"
    
    # Import storage
    from thoth.storage.backend import ThothStorage
    
    # Time initialization
    start = time.time()
    storage = ThothStorage(
        embedding_server_url="http://localhost:8765",
        use_vllm=True
    )
    await storage.initialize()
    init_time = time.time() - start
    print(f"✓ Storage initialized in {init_time:.2f}s")
    print(f"  Using: {storage.embedder.__class__.__name__}")
    if storage.chroma_collection:
        print(f"  Vectors: {storage.chroma_collection.count()}")
    print()
    
    # Test 1: Semantic search (most important - uses embeddings)
    print("1. Testing semantic search...")
    try:
        start = time.time()
        results = await storage.search_semantic(
            query="remote embedder client for external embedding services",
            limit=3
        )
        search_time = time.time() - start
        print(f"   ✓ Found {len(results)} results in {search_time:.2f}s")
        if results:
            print(f"   Top match: {results[0]['name']} (score: {results[0]['score']:.3f})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Basic symbol search (doesn't use embeddings)
    print("\n2. Testing symbol search...")
    try:
        from thoth.mcp.server import handle_call_tool
        start = time.time()
        result = await handle_call_tool("find_definition", {"name": "ThothStorage"})
        search_time = time.time() - start
        print(f"   ✓ Found definitions in {search_time:.2f}s")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    await storage.close()
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_tools())