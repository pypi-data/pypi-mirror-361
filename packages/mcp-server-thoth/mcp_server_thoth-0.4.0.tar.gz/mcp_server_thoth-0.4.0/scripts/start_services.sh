#!/bin/bash
# Script to start all Thoth services

echo "Starting Thoth services..."
echo ""
echo "This script will help you start the required services for optimal performance."
echo ""

# Function to check if a service is running
check_service() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ $service is already running on port $port"
        return 0
    else
        echo "✗ $service is not running on port $port"
        return 1
    fi
}

# Check TEI server
echo "1. Text Embeddings Inference (TEI) Server"
if check_service 8765 "TEI server"; then
    echo "   To verify: curl http://localhost:8765/health"
else
    echo "   To start: ./scripts/run_tei_server.sh"
    echo "   This provides fast embedding generation for semantic search"
fi
echo ""

# Check ChromaDB server (optional)
echo "2. ChromaDB Server (Optional - for even faster startup)"
if check_service 8000 "ChromaDB server"; then
    echo "   To verify: curl http://localhost:8000/api/v1/heartbeat"
else
    echo "   To start: ./scripts/run_chromadb_server.sh"
    echo "   This provides vector storage as a separate service"
    echo "   If not running, Thoth will use local ChromaDB (slightly slower startup)"
fi
echo ""

# Environment variables
echo "3. Environment Variables"
echo "   Set these before running the MCP server:"
echo ""
echo "   export THOTH_EMBEDDING_SERVER_URL=http://localhost:8765"
echo "   export THOTH_CHROMADB_SERVER_URL=http://localhost:8000  # Optional"
echo ""

# MCP server info
echo "4. MCP Server"
echo "   The MCP server will now start instantly (<1 second) with the above services running."
echo "   All heavy initialization (embeddings, vector DB) is handled by the external services."
echo ""

# Summary
echo "Summary:"
echo "- TEI server: Handles all embedding computations"
echo "- ChromaDB server (optional): Stores vector embeddings"
echo "- MCP server: Lightweight, starts instantly, connects to above services"
echo ""
echo "With this setup, the MCP server starts in <1 second instead of 30+ seconds!"