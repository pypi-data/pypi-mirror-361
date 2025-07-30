#!/usr/bin/env python3
"""Direct test of MCP tools without full server initialization."""

import asyncio
import os
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_mcp_tools():
    print("Testing MCP tools with TEI server...\n")
    
    # Set embedding server URL
    os.environ["THOTH_EMBEDDING_SERVER_URL"] = "http://localhost:8765"
    
    # Import after setting env var
    from thoth.storage.backend import ThothStorage
    from thoth.mcp.handlers import (
        find_definition,
        search_symbols,
        get_file_structure,
        search_semantic
    )
    
    # Initialize storage
    print("1. Initializing storage with remote embeddings...")
    storage = ThothStorage(
        embedding_server_url="http://localhost:8765",
        use_vllm=True
    )
    await storage.initialize()
    print(f"   ✓ Storage initialized with {storage.embedder.__class__.__name__}")
    
    # Test basic tools
    print("\n2. Testing find_definition...")
    try:
        results = await find_definition(storage, "ThothStorage")
        print(f"   ✓ Found {len(results)} definitions")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n3. Testing search_symbols...")
    try:
        results = await search_symbols(storage, "embed", type_filter="function")
        print(f"   ✓ Found {len(results)} symbols")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n4. Testing semantic search (the critical one!)...")
    try:
        results = await search_semantic(storage, "function that handles remote embedding requests", limit=5)
        print(f"   ✓ Found {len(results)} results")
        if results:
            print(f"   Top result: {results[0].name} in {results[0].file_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Check storage stats
    print("\n5. Storage stats:")
    stats = await storage.get_stats()
    print(f"   - Embedding type: {stats['embedding_type']}")
    print(f"   - Total symbols: {stats['total_symbols']}")
    print(f"   - Vector count: {stats.get('vector_count', 0)}")
    
    await storage.close()
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())