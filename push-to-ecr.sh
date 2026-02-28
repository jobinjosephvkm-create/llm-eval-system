#!/bin/bash

# AWS ECR Registry and Region
REGISTRY="963777256515.dkr.ecr.eu-north-1.amazonaws.com"
REGION="eu-north-1"

# List of services to build and push
SERVICES=("orchestrator" "agent" "judge" "optimiser" "ollama")

# Enable Docker Buildx
echo "Setting up Docker Buildx..."
docker buildx create --use 2>/dev/null || docker buildx use default

# Login to ECR
echo "Logging in to AWS ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY
if [ $? -ne 0 ]; then
    echo "ECR login failed. Exiting."
    exit 1
fi

# Build and push each service with multi-architecture support
for SERVICE in "${SERVICES[@]}"; do
    ECR_IMAGE="$REGISTRY/llm-eval-system-$SERVICE:latest"
    
    echo "Building and pushing $SERVICE (multi-arch: linux/amd64,linux/arm64)..."
    
    # Check if Dockerfile exists
    if [ ! -f "$SERVICE/Dockerfile" ]; then
        echo "Warning: $SERVICE/Dockerfile not found. Skipping..."
        continue
    fi
    
    # Build and push multi-architecture image
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f $SERVICE/Dockerfile \
        -t $ECR_IMAGE \
        --push $SERVICE/
    
    if [ $? -ne 0 ]; then
        echo "Failed to build/push $SERVICE."
    else
        echo "Successfully built and pushed $ECR_IMAGE!"
    fi
done

echo "All done!"
