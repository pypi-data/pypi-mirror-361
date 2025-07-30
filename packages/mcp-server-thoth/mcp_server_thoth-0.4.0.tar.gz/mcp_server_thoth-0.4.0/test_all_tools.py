#!/usr/bin/env python3
"""Test all MCP tools."""

import asyncio
import os
from thoth.mcp.server import handle_call_tool

async def test_all_tools():
    print("Testing ALL MCP tools with TEI server...\n")
    
    # Set embedding server URL
    os.environ["THOTH_EMBEDDING_SERVER_URL"] = "http://localhost:8765"
    
    # 1. Test find_definition (doesn't need embeddings)
    print("1. Testing find_definition...")
    try:
        result = await handle_call_tool("find_definition", {
            "name": "ThothStorage"
        })
        print(f"   ✓ Found {len(result)} definitions")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Test search_symbols (doesn't need embeddings)
    print("\n2. Testing search_symbols...")
    try:
        result = await handle_call_tool("search_symbols", {
            "query": "embed",
            "type_filter": "function"
        })
        print(f"   ✓ Found {len(result)} symbols")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 3. Test get_file_structure (doesn't need embeddings)
    print("\n3. Testing get_file_structure...")
    try:
        result = await handle_call_tool("get_file_structure", {
            "file_path": "thoth/storage/backend.py",
            "repo": "thoth"
        })
        print(f"   ✓ Got file structure")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 4. Test get_callers (doesn't need embeddings)
    print("\n4. Testing get_callers...")
    try:
        result = await handle_call_tool("get_callers", {
            "name": "encode"
        })
        print(f"   ✓ Found {len(result)} callers")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 5. Test get_repositories (doesn't need embeddings)
    print("\n5. Testing get_repositories...")
    try:
        result = await handle_call_tool("get_repositories", {})
        print(f"   ✓ Found {len(result)} repositories")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 6. Test semantic_search (NEEDS embeddings - the critical one!)
    print("\n6. Testing search_semantic (uses embeddings)...")
    try:
        result = await handle_call_tool("search_semantic", {
            "query": "function that handles remote embedding requests",
            "limit": 5
        })
        print(f"   ✓ Found {len(result)} results")
        if result and len(result) > 0:
            # Show top result
            lines = result[0].text.split('\n')
            print(f"   Top result: {lines[0]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 7. Test development memory tools
    print("\n7. Testing start_dev_session...")
    try:
        result = await handle_call_tool("start_dev_session", {
            "branch": "test-branch",
            "description": "Testing MCP tools"
        })
        print(f"   ✓ Started session")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n8. Testing check_approach...")
    try:
        result = await handle_call_tool("check_approach", {
            "approach": "Using RemoteEmbedder for embeddings"
        })
        print(f"   ✓ Checked approach")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\nAll tools tested!")

if __name__ == "__main__":
    asyncio.run(test_all_tools())