#!/bin/bash
# Script to run the vLLM embedding server separately

echo "Starting vLLM embedding server..."
echo "This server provides embeddings for semantic search in Thoth."
echo ""
echo "The server will listen on port 8765 by default."
echo "Set THOTH_EMBEDDING_SERVER_URL in the MCP server to connect."
echo ""

# Run the embedding server
python -m thoth.embeddings.vllm_server --host 0.0.0.0 --port 8765