# LLM Evaluation System

A distributed LLM evaluation system with multiple microservices for agent, judge, optimiser, and orchestrator components.

## Architecture

The system consists of 5 main services:

- **Ollama**: LLM serving service (port 11434)
- **Agent**: Agent service (port 8001)
- **Judge**: Judge service (port 8002)
- **Optimiser**: Optimiser service (port 8003)
- **Orchestrator**: Orchestrator service (port 8004)
 - **Langfuse**: Observability dashboard for LLM traces (port 3000)

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Setup

Run the setup script to build and start all services:

```bash
./setup.sh
```

This will:
- Check for Docker and Docker Compose
- Build all service containers
- Start all services
- Verify service health
- Display service URLs and useful commands

### Manual Setup

If you prefer to set up manually:

```bash
# Build and start services
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Service URLs

Once running, services are available at:

- **Ollama**: http://localhost:11434
- **Agent**: http://localhost:8001
- **Judge**: http://localhost:8002
- **Optimiser**: http://localhost:8003
- **Orchestrator**: http://localhost:8004
 - **Langfuse (observability)**: http://localhost:3000

## Useful Commands

```bash
# View logs for a specific service
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Check service status
docker-compose ps

# Pull a model in Ollama
docker exec -it ollama ollama pull llama2
docker exec -it ollama ollama pull mistral
```

## Development

Each service has its own directory with:
- `Dockerfile`: Container configuration
- `main.py`: Service implementation
- `requirements.txt`: Python dependencies

To modify a service:
1. Edit the files in the service directory
2. Rebuild: `docker-compose build [service_name]`
3. Restart: `docker-compose up -d [service_name]`

## Troubleshooting

- If a service fails to start, check logs: `docker-compose logs [service_name]`
- Ensure ports 11434, 8001-8004 are available
- Make sure Docker has sufficient resources allocated
