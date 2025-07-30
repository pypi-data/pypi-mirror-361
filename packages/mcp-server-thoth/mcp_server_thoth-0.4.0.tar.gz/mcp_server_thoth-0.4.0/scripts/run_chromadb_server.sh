#!/bin/bash
# Script to run ChromaDB server using Docker

echo "Starting ChromaDB server..."
echo ""
echo "This will:"
echo "- Pull the official ChromaDB Docker image"
echo "- Run ChromaDB server on port 8000"
echo "- Use persistent storage in ~/.thoth/chroma_data"
echo ""

# Create directory if it doesn't exist
mkdir -p ~/.thoth/chroma_data

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q '^thoth-chromadb$'; then
    echo "Found existing thoth-chromadb container"
    
    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q '^thoth-chromadb$'; then
        echo "ChromaDB server is already running"
        exit 0
    else
        echo "Starting existing container..."
        docker start thoth-chromadb
    fi
else
    # Run ChromaDB server using Docker
    echo "Starting ChromaDB server on http://localhost:8000"
    echo "Data directory: ~/.thoth/chroma_data"
    echo ""
    
    docker run -d \
        --name thoth-chromadb \
        -p 8000:8000 \
        -v ~/.thoth/chroma_data:/chroma/chroma \
        -e IS_PERSISTENT=TRUE \
        -e PERSIST_DIRECTORY=/chroma/chroma \
        -e ANONYMIZED_TELEMETRY=FALSE \
        --restart unless-stopped \
        chromadb/chroma:latest
fi

echo ""
echo "ChromaDB server starting..."
echo "Check status with: docker ps | grep thoth-chromadb"
echo "View logs with: docker logs thoth-chromadb"
echo "Stop with: docker stop thoth-chromadb"