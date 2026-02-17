#!/bin/bash

# Build Script for CI/CD Pipeline
# This script builds and tests the Docker image

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="cicd-demo"
DOCKER_REGISTRY="docker.io/yourorg"
IMAGE_TAG=${1:-latest}

echo -e "${GREEN}Building Docker image...${NC}"
docker build -t ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG} -f ../application/Dockerfile ../application/

echo -e "${GREEN}Running tests...${NC}"
docker run --rm ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG} pytest /app/tests/

echo -e "${GREEN}Tagging image...${NC}"
docker tag ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${APP_NAME}:latest

echo -e "${GREEN}Build completed successfully!${NC}"
