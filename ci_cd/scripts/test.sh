#!/bin/bash

# Test Script for CI/CD Pipeline
# Runs all tests with coverage

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Running CI/CD Tests...${NC}"
cd ../application

echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${YELLOW}Running linting...${NC}"
pylint src/ || true
flake8 src/ || true

echo -e "${YELLOW}Running unit tests with coverage...${NC}"
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo -e "${GREEN}Tests completed!${NC}"
echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
