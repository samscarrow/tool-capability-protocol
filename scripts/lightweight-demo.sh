#!/bin/bash

echo "🚀 Starting Lightweight TCP Security System"
echo "==========================================="

# Start Ollama in background
echo "Starting Ollama service..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama ready!"
        break
    fi
    sleep 1
done

# Pull lightweight model
echo "📥 Pulling lightweight model (llama3.2:1b)..."
ollama pull llama3.2:1b

echo ""
echo "🔐 TCP Security System Ready!"
echo "============================="
echo ""

# Run full system demonstration
echo "🎬 Running Full System Encode with Lightweight LLM"
echo ""

# Run the lightweight demo Python script
echo "Starting lightweight TCP security demonstration..."
python3 /tcp-security/run-lightweight-demo.py

echo ""
echo "🎉 Demonstration complete!"
echo "Results saved in /tcp-security/lightweight_encode_results.json"

# Keep container running
echo ""
echo "📋 Container ready for interactive use!"
echo "Available commands:"
echo "  python3 tcp/local_ollama_demo.py"
echo "  python3 run-lightweight-demo.py"
echo "  ollama list"
echo "  cat lightweight_encode_results.json"
echo ""
echo "Press Ctrl+C to stop, then 'exit' to close container"

# Monitor and keep alive
tail -f /tmp/ollama.log