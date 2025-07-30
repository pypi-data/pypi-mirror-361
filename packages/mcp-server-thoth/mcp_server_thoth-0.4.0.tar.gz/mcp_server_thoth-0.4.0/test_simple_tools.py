#!/usr/bin/env python3
"""Simple test of MCP semantic search."""

import asyncio
import os
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_semantic_search():
    print("Testing semantic search with TEI server...\n")
    
    # Set embedding server URL
    os.environ["THOTH_EMBEDDING_SERVER_URL"] = "http://localhost:8765"
    
    # Import storage backend
    from thoth.storage.backend import ThothStorage
    
    # Initialize storage
    print("1. Initializing storage...")
    storage = ThothStorage(
        embedding_server_url="http://localhost:8765",
        use_vllm=True
    )
    await storage.initialize()
    print(f"   ✓ Using {storage.embedder.__class__.__name__}")
    
    # Test semantic search directly
    print("\n2. Testing semantic search...")
    try:
        results = await storage.search_semantic(
            query="remote embedding client implementation",
            limit=5
        )
        print(f"   ✓ Found {len(results)} results")
        
        if results:
            print("\n   Top results:")
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. {result['name']} ({result['type']}) in {result['file_path']}")
                print(f"      Score: {result['score']:.3f}")
        else:
            print("   No results found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    await storage.close()

if __name__ == "__main__":
    asyncio.run(test_semantic_search())