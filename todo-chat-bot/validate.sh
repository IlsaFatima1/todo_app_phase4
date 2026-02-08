#!/bin/bash
# Validation script for Todo Chat Bot deployment

set -e

echo "🔍 Validating Todo Chat Bot deployment prerequisites..."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

check_minikube_running() {
    if minikube status &> /dev/null; then
        echo -e "${GREEN}✓${NC} Minikube is running"
        return 0
    else
        echo -e "${RED}✗${NC} Minikube is not running"
        return 1
    fi
}

check_docker_images() {
    eval $(minikube docker-env)

    if docker images | grep -q "todo-frontend"; then
        echo -e "${GREEN}✓${NC} Frontend image found"
    else
        echo -e "${YELLOW}⚠${NC} Frontend image not found (will need to build)"
    fi

    if docker images | grep -q "todo-backend"; then
        echo -e "${GREEN}✓${NC} Backend image found"
    else
        echo -e "${YELLOW}⚠${NC} Backend image not found (will need to build)"
    fi
}

# Run checks
echo "Checking required tools..."
check_command "minikube" || exit 1
check_command "kubectl" || exit 1
check_command "helm" || exit 1
check_command "docker" || exit 1

echo ""
echo "Checking Minikube status..."
check_minikube_running || exit 1

echo ""
echo "Checking Docker images..."
check_docker_images

echo ""
echo "Validating Helm chart..."
if helm lint todo-chat-bot; then
    echo -e "${GREEN}✓${NC} Helm chart validation passed"
else
    echo -e "${RED}✗${NC} Helm chart validation failed"
    exit 1
fi

echo ""
echo "Testing Helm template rendering..."
if helm template todo-app todo-chat-bot -f values-local.yaml > /dev/null; then
    echo -e "${GREEN}✓${NC} Helm template rendering successful"
else
    echo -e "${RED}✗${NC} Helm template rendering failed"
    exit 1
fi

echo ""
echo "Checking Kubernetes cluster connectivity..."
if kubectl cluster-info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Kubernetes cluster is accessible"
else
    echo -e "${RED}✗${NC} Cannot connect to Kubernetes cluster"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All validation checks passed!${NC}"
echo ""
echo "You can now proceed with deployment:"
echo "  ./deploy-local.sh"