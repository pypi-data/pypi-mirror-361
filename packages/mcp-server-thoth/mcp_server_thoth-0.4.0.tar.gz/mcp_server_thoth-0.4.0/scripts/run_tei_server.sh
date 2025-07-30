#!/bin/bash
# Script to run Text Embeddings Inference (TEI) server with Qwen3-Embedding-0.6B

echo "Starting Text Embeddings Inference server with Qwen3-Embedding-0.6B..."
echo ""
echo "This will:"
echo "- Pull the TEI Docker image if not present"
echo "- Download the model on first run (~1.2GB for ONNX)"
echo "- Start the server on port 8765"
echo ""

# Check if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    echo "GPU detected, using GPU version..."
    # Run TEI with GPU (CUDA ONNX version)
    docker run --gpus all -p 8765:80 \
      -v $HOME/.cache/huggingface:/data \
      --pull always \
      ghcr.io/huggingface/text-embeddings-inference:cuda-1.7 \
      --model-id Qwen/Qwen3-Embedding-0.6B \
      --revision refs/pr/27 \
      --max-batch-tokens 512
else
    echo "No GPU detected, using CPU version..."
    # Run TEI with CPU (ONNX version)
    docker run -p 8765:80 \
      -v $HOME/.cache/huggingface:/data \
      --pull always \
      ghcr.io/huggingface/text-embeddings-inference:cpu-1.7 \
      --model-id Qwen/Qwen3-Embedding-0.6B \
      --revision refs/pr/27 \
      --max-batch-tokens 512
fi