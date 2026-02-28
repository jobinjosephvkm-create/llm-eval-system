#!/bin/bash

# LLM Evaluation System Setup Script
# This script sets up the entire LLM evaluation system with all services

set -e  # Exit on any error

echo "🚀 Setting up LLM Evaluation System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Build and start all services
echo "🔨 Building and starting services..."
if command -v docker-compose &> /dev/null; then
    docker-compose build
    docker-compose up -d
else
    docker compose build
    docker compose up -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
services=("ollama:11434" "agent:8001" "judge:8002" "optimiser:8003" "orchestrator:8004")

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -s "http://localhost:$port" > /dev/null 2>&1 || [ "$service_name" = "ollama" ]; then
        echo "✅ $service_name is running"
    else
        echo "❌ $service_name is not responding on port $port"
    fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Service URLs:"
echo "  - Ollama: http://localhost:11434"
echo "  - Agent: http://localhost:8001"
echo "  - Judge: http://localhost:8002"
echo "  - Optimiser: http://localhost:8003"
echo "  - Orchestrator: http://localhost:8004"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f [service_name]"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Check status: docker-compose ps"
echo ""
echo "📖 To pull a model in Ollama:"
echo "  docker exec -it ollama ollama pull llama2"
echo "  docker exec -it ollama ollama pull mistral"
echo ""
