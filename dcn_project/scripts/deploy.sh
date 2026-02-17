#!/bin/bash

# DCN Deployment Script
# Deploys the Data Collection Node system to Kubernetes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="dcn"
ENVIRONMENT=${1:-production}
IMAGE_TAG=${2:-latest}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   DCN Deployment Script${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}Environment:${NC} $ENVIRONMENT"
echo -e "${YELLOW}Image Tag:${NC} $IMAGE_TAG"
echo -e "${YELLOW}Namespace:${NC} $NAMESPACE"
echo ""

# Check prerequisites
echo -e "${GREEN}[1/10] Checking prerequisites...${NC}"
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Create namespace
echo -e "${GREEN}[2/10] Creating namespace...${NC}"
kubectl apply -f ../kubernetes/namespace.yaml
echo ""

# Deploy RBAC
echo -e "${GREEN}[3/10] Deploying RBAC resources...${NC}"
kubectl apply -f ../kubernetes/rbac/rbac.yaml
echo ""

# Deploy secrets
echo -e "${GREEN}[4/10] Deploying secrets...${NC}"
echo -e "${YELLOW}⚠️  Warning: Update secrets before production deployment!${NC}"
kubectl apply -f ../kubernetes/secrets/dcn-secrets.yaml
echo ""

# Deploy ConfigMaps
echo -e "${GREEN}[5/10] Deploying ConfigMaps...${NC}"
kubectl apply -f ../kubernetes/configmaps/
echo ""

# Deploy infrastructure (Kafka, TimescaleDB, Redis)
echo -e "${GREEN}[6/10] Deploying infrastructure services...${NC}"
echo -e "${YELLOW}Deploying Kafka...${NC}"
kubectl apply -f ../kubernetes/statefulsets/kafka-statefulset.yaml
echo -e "${YELLOW}Deploying TimescaleDB...${NC}"
kubectl apply -f ../kubernetes/statefulsets/timescaledb-statefulset.yaml

# Wait for infrastructure
echo -e "${YELLOW}Waiting for infrastructure to be ready (this may take a few minutes)...${NC}"
kubectl wait --for=condition=ready pod -l app=kafka -n $NAMESPACE --timeout=300s || true
kubectl wait --for=condition=ready pod -l app=timescaledb -n $NAMESPACE --timeout=300s || true
echo ""

# Deploy application services
echo -e "${GREEN}[7/10] Deploying DCN services...${NC}"
kubectl apply -f ../kubernetes/deployments/collector-deployment.yaml
kubectl apply -f ../kubernetes/deployments/api-deployment.yaml
echo ""

# Deploy services
echo -e "${GREEN}[8/10] Deploying Kubernetes services...${NC}"
kubectl apply -f ../kubernetes/services/
echo ""

# Deploy Ingress
echo -e "${GREEN}[9/10] Deploying Ingress...${NC}"
kubectl apply -f ../kubernetes/ingress/dcn-ingress.yaml
echo ""

# Deploy HPA
echo -e "${GREEN}[10/10] Deploying HorizontalPodAutoscalers...${NC}"
kubectl apply -f ../kubernetes/hpa/dcn-hpa.yaml
echo ""

# Deploy monitoring (if available)
if [ -d "../kubernetes/monitoring" ]; then
    echo -e "${GREEN}[11/10] Deploying monitoring resources...${NC}"
    kubectl apply -f ../kubernetes/monitoring/
    echo ""
fi

# Wait for deployments
echo -e "${GREEN}Waiting for deployments to be ready...${NC}"
kubectl rollout status deployment/dcn-collector -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/dcn-api -n $NAMESPACE --timeout=300s
echo ""

# Display deployment status
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   Deployment Status${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

echo -e "${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE -o wide
echo ""

echo -e "${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE
echo ""

echo -e "${YELLOW}Ingress:${NC}"
kubectl get ingress -n $NAMESPACE
echo ""

# Get API endpoint
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   DCN Endpoints${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

API_IP=$(kubectl get svc dcn-api -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
INGRESS_HOST=$(kubectl get ingress dcn-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "not configured")

if [ "$API_IP" != "pending" ]; then
    echo -e "${YELLOW}API LoadBalancer:${NC} http://$API_IP"
    echo -e "${YELLOW}Health Check:${NC} http://$API_IP/health"
    echo -e "${YELLOW}API Docs:${NC} http://$API_IP/docs"
    
    # Test health endpoint
    echo ""
    echo -e "${GREEN}Testing health endpoint...${NC}"
    sleep 10  # Wait for LB to be ready
    if curl -f -s "http://$API_IP/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Health check failed (service may still be starting)${NC}"
    fi
fi

if [ "$INGRESS_HOST" != "not configured" ]; then
    echo ""
    echo -e "${YELLOW}Ingress Hostname:${NC} https://$INGRESS_HOST"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   Deployment Completed Successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Monitor pods: ${NC}kubectl get pods -n $NAMESPACE -w"
echo -e "  2. View logs: ${NC}kubectl logs -n $NAMESPACE -l app=dcn-api -f"
echo -e "  3. Port forward: ${NC}kubectl port-forward -n $NAMESPACE svc/dcn-api 8080:80"
echo -e "  4. Access API: ${NC}http://localhost:8080"
echo -e "  5. View metrics: ${NC}kubectl port-forward -n $NAMESPACE svc/dcn-api 8080:80 & curl http://localhost:8080/metrics"
echo ""
