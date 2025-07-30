# Thoth Architecture: Separation of Concerns

## Overview

Thoth v0.3+ implements a clean separation of concerns between the MCP server and resource-intensive services like the embedding model. This allows for:

- Fast MCP server startup (< 1 second)
- Independent scaling of services
- Optional features without performance penalty
- Better resource management

## Components

### 1. MCP Server (Lightweight)
The main MCP server is now lightweight and starts instantly:
- SQLite database access
- Graph operations (NetworkX)
- Remote embedding client
- Development memory tracking

### 2. Embedding Server (Heavy)
The vLLM embedding server runs separately:
- Loads Qwen3-Embedding-0.6B model (1.1GB)
- Provides OpenAI-compatible API
- Can be shared across multiple MCP instances
- Optional - falls back to TF-IDF if not available

### 3. Storage Layer
- ChromaDB for vector storage
- SQLite for structured data
- NetworkX for graph relationships
- Redis for optional caching

## Running the Services

### Step 1: Start the Embedding Server
```bash
# In a separate terminal
./scripts/run_embedding_server.sh
# Or directly:
python -m thoth.embeddings.vllm_server --port 8765
```

The embedding server will:
- Load the vLLM model (takes 20-30 seconds)
- Listen on port 8765
- Provide health check at `/health`
- Expose embeddings at `/v1/embeddings`

### Step 2: Configure MCP Server
Set the embedding server URL:
```bash
export THOTH_EMBEDDING_SERVER_URL=http://localhost:8765
```

### Step 3: Start MCP Server
The MCP server will now start instantly and connect to the embedding server when needed.

## Fallback Behavior

If the embedding server is not available:
- MCP server still starts successfully
- Falls back to TF-IDF embeddings
- All features remain functional
- Lower quality semantic search

## Benefits

1. **Fast Startup**: MCP server starts in < 1 second
2. **Resource Efficiency**: Model loaded only when needed
3. **Scalability**: Can run embedding server on GPU machine
4. **Flexibility**: Easy to swap embedding models
5. **Reliability**: Graceful fallback to TF-IDF

## Environment Variables

- `THOTH_EMBEDDING_SERVER_URL`: URL of the embedding server (default: `http://localhost:8765`)