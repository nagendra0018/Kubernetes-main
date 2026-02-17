#!/bin/bash

# CI/CD Project Rollback Script
# This script rolls back the deployment to previous version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="cicd-demo"
ENVIRONMENT=${1:-prod}
REVISION=${2:-0}

echo -e "${RED}======================================${NC}"
echo -e "${RED}   CI/CD Rollback Script${NC}"
echo -e "${RED}======================================${NC}"
echo ""
echo -e "${YELLOW}Application:${NC} $APP_NAME"
echo -e "${YELLOW}Environment:${NC} $ENVIRONMENT"
echo -e "${YELLOW}Revision:${NC} $REVISION (0 = previous)"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|test|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Use dev, test, or prod${NC}"
    exit 1
fi

# Confirm rollback for production
if [ "$ENVIRONMENT" == "prod" ]; then
    echo -e "${RED}WARNING: You are about to rollback PRODUCTION!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Rollback cancelled${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}[1/5] Checking deployment history...${NC}"
kubectl rollout history deployment/${APP_NAME} -n ${ENVIRONMENT}
echo ""

echo -e "${GREEN}[2/5] Getting current status...${NC}"
kubectl get deployment ${APP_NAME} -n ${ENVIRONMENT}
echo ""

echo -e "${GREEN}[3/5] Rolling back deployment...${NC}"
if [ "$REVISION" == "0" ]; then
    kubectl rollout undo deployment/${APP_NAME} -n ${ENVIRONMENT}
else
    kubectl rollout undo deployment/${APP_NAME} -n ${ENVIRONMENT} --to-revision=${REVISION}
fi
echo ""

echo -e "${GREEN}[4/5] Waiting for rollback to complete...${NC}"
kubectl rollout status deployment/${APP_NAME} -n ${ENVIRONMENT} --timeout=5m
echo ""

echo -e "${GREEN}[5/5] Verifying rollback...${NC}"
kubectl get pods -n ${ENVIRONMENT} -l app=${APP_NAME}
echo ""

# Health check
SERVICE_IP=$(kubectl get svc ${APP_NAME} -n ${ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$SERVICE_IP" != "pending" ]; then
    echo -e "${GREEN}Running health check...${NC}"
    sleep 10  # Wait for pods to be ready
    if curl -f -s "http://${SERVICE_IP}/health" > /dev/null; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   Rollback Completed Successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
