#!/bin/bash

# CI/CD Project Deployment Script
# This script deploys the application to specified environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="cicd-demo"
DOCKER_REGISTRY="docker.io/yourorg"
ENVIRONMENT=${1:-dev}
IMAGE_TAG=${2:-latest}

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   CI/CD Deployment Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Application:${NC} $APP_NAME"
echo -e "${YELLOW}Environment:${NC} $ENVIRONMENT"
echo -e "${YELLOW}Image Tag:${NC} $IMAGE_TAG"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|test|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Use dev, test, or prod${NC}"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if ansible-playbook is available
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}Error: ansible-playbook is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}[1/6] Validating Kubernetes connection...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Kubernetes connection successful${NC}"
echo ""

echo -e "${GREEN}[2/6] Creating namespace if not exists...${NC}"
kubectl apply -f ../kubernetes/${ENVIRONMENT}/namespace.yaml
echo ""

echo -e "${GREEN}[3/6] Deploying application using Ansible...${NC}"
ansible-playbook \
    ../ansible/playbooks/deploy-to-k8s.yml \
    -i ../ansible/inventory/${ENVIRONMENT}.ini \
    -e "image_tag=${IMAGE_TAG}" \
    -e "environment=${ENVIRONMENT}"
echo ""

echo -e "${GREEN}[4/6] Waiting for deployment to be ready...${NC}"
kubectl rollout status deployment/${APP_NAME} -n ${ENVIRONMENT} --timeout=5m
echo ""

echo -e "${GREEN}[5/6] Verifying deployment...${NC}"
PODS=$(kubectl get pods -n ${ENVIRONMENT} -l app=${APP_NAME} --no-headers | wc -l)
echo -e "${YELLOW}Running pods:${NC} $PODS"
kubectl get pods -n ${ENVIRONMENT} -l app=${APP_NAME}
echo ""

echo -e "${GREEN}[6/6] Getting service endpoint...${NC}"
SERVICE_IP=$(kubectl get svc ${APP_NAME} -n ${ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
echo -e "${YELLOW}Service endpoint:${NC} $SERVICE_IP"
echo ""

# Run health check if service IP is available
if [ "$SERVICE_IP" != "pending" ]; then
    echo -e "${GREEN}Running health check...${NC}"
    if curl -f -s "http://${SERVICE_IP}/health" > /dev/null; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Health check failed (service may still be starting)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   Deployment Completed Successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Monitor pods: ${NC}kubectl get pods -n ${ENVIRONMENT} -w"
echo -e "  2. View logs: ${NC}kubectl logs -n ${ENVIRONMENT} -l app=${APP_NAME} -f"
echo -e "  3. Check service: ${NC}kubectl get svc ${APP_NAME} -n ${ENVIRONMENT}"
if [ "$SERVICE_IP" != "pending" ]; then
    echo -e "  4. Access app: ${NC}http://${SERVICE_IP}"
fi
echo ""
