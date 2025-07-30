# Thoth Setup Guide

## Quick Start

The complete setup sequence for Thoth is:

```bash
# 1. Build the package
uv build

# 2. Initialize Thoth (starts external services automatically)
uv run thoth-cli init

# 3. Source the environment variables
source ~/.thoth/env

# 4. Index your codebase
uv run thoth-cli index thoth .

# 5. Add to Claude Desktop
claude mcp add thoth -s user -- uvx --python 3.12 mcp-server-thoth
```

## What `thoth-cli init` Does

The `init` command handles the complete setup:

1. **Creates database** - SQLite database for storing code structure
2. **Creates directories** - `~/.thoth/`, logs, cache directories  
3. **Starts TEI server** - Text Embeddings Inference for fast embeddings (requires Docker)
4. **Creates environment file** - Sets up `THOTH_EMBEDDING_SERVER_URL` and optionally `THOTH_CHROMADB_SERVER_URL`
5. **Verifies installation** - Checks all modules load correctly

## Architecture

With the new architecture, Thoth uses a complete separation of concerns:

- **MCP Server**: Lightweight, starts in <1 second
- **TEI Server**: Handles all embedding computations (runs on port 8765)
- **ChromaDB Server**: Vector storage as a separate service (runs on port 8000)

This architecture ensures:
- ✅ MCP server starts instantly (<1 second vs 30+ seconds)
- ✅ Embeddings are computed by dedicated service
- ✅ Vector storage runs as independent service
- ✅ Services can be restarted without losing data
- ✅ Clean microservices architecture

## Manual Service Management

If you prefer to manage services manually:

```bash
# Start without services
uv run thoth-cli init --no-start-services

# Start TEI server manually
./scripts/run_tei_server.sh

# (Optional) Start ChromaDB server
./scripts/run_chromadb_server.sh

# Set environment variables
export THOTH_EMBEDDING_SERVER_URL=http://localhost:8765
export THOTH_CHROMADB_SERVER_URL=http://localhost:8000  # optional
```

## Check Status

To verify everything is running:

```bash
uv run thoth-cli status
```

This will show:
- Database status and size
- TEI server status and embedding test
- ChromaDB server status
- Environment file location
- Indexed repositories

## Troubleshooting

### Docker not found
The TEI server requires Docker. Install from: https://docs.docker.com/get-docker/

### TEI server won't start
- Check if port 8765 is already in use
- Check Docker daemon is running: `docker ps`
- Check logs: `docker logs $(docker ps -q --filter ancestor=ghcr.io/huggingface/text-embeddings-inference)`

### Slow first startup
The first time TEI starts, it downloads the Qwen3-Embedding model (~1.2GB). Subsequent starts are much faster.

### MCP server still slow
Make sure you've sourced the environment file:
```bash
source ~/.thoth/env
```

Or set the variable manually:
```bash
export THOTH_EMBEDDING_SERVER_URL=http://localhost:8765
```