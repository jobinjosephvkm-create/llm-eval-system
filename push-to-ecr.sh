#!/bin/bash

# AWS ECR Registry and Region
REGISTRY="963777256515.dkr.ecr.eu-north-1.amazonaws.com"
REGION="eu-north-1"

# List of services to build and push
SERVICES=("orchestrator" "agent" "judge" "optimiser" "ollama")

# Enable Docker Buildx
echo "Setting up Docker Buildx..."
docker buildx create --use 2>/dev/null || docker buildx use default

# Smart ECR login - check if already logged in
echo "Checking ECR login status..."
if ! docker info | grep -q "Username"; then
    echo "Logging in to AWS ECR..."
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY
    if [ $? -ne 0 ]; then
        echo "ECR login failed. Exiting."
        exit 1
    fi
else
    echo "Already logged into ECR!"
fi

# Build and push each service with multi-architecture support
for SERVICE in "${SERVICES[@]}"; do
    ECR_IMAGE="$REGISTRY/llm-eval-system-$SERVICE:latest"
    
    echo "Building and pushing $SERVICE (multi-arch: linux/amd64,linux/arm64)..."
    
    # Check if Dockerfile exists
    if [ ! -f "$SERVICE/Dockerfile" ]; then
        echo "Dockerfile not found for $SERVICE. Skipping..."
        continue
    fi
    
    # Build and push with multi-architecture support
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f $SERVICE/Dockerfile \
        -t $ECR_IMAGE \
        --push $SERVICE/
    
    if [ $? -ne 0 ]; then
        echo "Failed to build/push $SERVICE."
    else
        echo "Successfully built and pushed $SERVICE!"
    fi
done

echo " All services processed!"
