#!/bin/bash

# LLM Evaluation System Setup Script
# Usage: ./setup.sh [command]
# Commands: clean, build, start, stop, restart, status, logs

set -e  # Exit on any error

# Show usage if no arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 {clean|build|start|stop|restart|status|logs}"
    echo ""
    echo "Commands:"
    echo "  clean   - Remove all containers and images"
    echo "  build   - Build all images locally"
    echo "  build [service] - Build a specific service (e.g., build orchestrator)"
    echo "  start   - Start all services (default)"
    echo "  stop    - Stop all services"
    echo "  restart - Restart all services"
    echo "  status  - Show service status"
    echo "  logs    - Show service logs"
    exit 0
fi

COMMAND=${1:-"start"}

case $COMMAND in
    clean)
        echo "🧹 Cleaning up Docker environment..."
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
        docker system prune -f
        docker builder prune -f
        docker rmi $(docker images -q) 2>/dev/null || true  # Remove all images
        echo "✅ Cleanup complete! Removed containers, images, and cache."
        ;;
    
    build)
        # Check if a specific service is requested
        if [ -n "$2" ]; then
            SERVICE="$2"
            echo "📦 Building $SERVICE service..."
            if command -v docker-compose &> /dev/null; then
                docker-compose build --no-cache "$SERVICE"
            else
                docker compose build --no-cache "$SERVICE"
            fi
            echo "✅ Build complete for $SERVICE!"
        else
            echo "📦 Building all images locally..."
            if command -v docker-compose &> /dev/null; then
                docker-compose build --no-cache
            else
                docker compose build --no-cache
            fi
            echo "✅ Build complete!"
        fi
        ;;
    
    start)
        echo "🚀 Starting LLM Evaluation System..."
        
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

        # Ensure the phi3 model is pulled into Ollama
        echo "📥 Ensuring 'phi3' model is available in Ollama..."
        if docker ps --format '{{.Names}}' | grep -q '^ollama$'; then
            # Non-interactive pull; ignore failure so setup can continue
            docker exec ollama ollama pull phi3 || echo "⚠️  Failed to pull 'phi3' model automatically. You can run: docker exec -it ollama ollama pull phi3"
        else
            echo "⚠️  Ollama container not running; skipping automatic model pull."
        fi

        # Check if services are running
        echo "🔍 Checking service status..."
        services=("ollama:11434" "agent:8001" "judge:8002" "optimiser:8003" "orchestrator:8004" "langfuse:3000")
        
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
        echo "  - View logs: $0 logs [service_name]"
        echo "  - Stop services: $0 stop"
        echo "  - Restart services: $0 restart"
        echo "  - Check status: $0 status"
        echo "  - Build images: $0 build"
        echo ""
        echo "📖 To pull models in Ollama manually:"
        echo "  docker exec -it ollama ollama pull phi3"
        echo "  docker exec -it ollama ollama pull llama2"
        echo "  docker exec -it ollama ollama pull mistral"
        ;;
    
    stop)
        echo "🛑 Stopping all services..."
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
        echo "✅ All services stopped!"
        ;;
    
    restart)
        echo "🔄 Restarting all services..."
        docker-compose restart 2>/dev/null || docker compose restart 2>/dev/null || true
        echo "✅ Services restarted!"
        ;;
    
    status)
        echo "📊 Service Status:"
        docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null || true
        ;;
    
    logs)
        if [ -z "$2" ]; then
            echo "📋 Showing logs for all services:"
            docker-compose logs 2>/dev/null || docker compose logs 2>/dev/null || true
        else
            echo "📋 Showing logs for $2:"
            docker-compose logs -f "$2" 2>/dev/null || docker compose logs -f "$2" 2>/dev/null || true
        fi
        ;;
    
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Use: $0 {clean|build|start|stop|restart|status|logs}"
        exit 1
        ;;
esac
