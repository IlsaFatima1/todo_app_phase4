#!/bin/bash
# Local deployment script for Todo Chat Bot on Minikube

set -e

echo "🚀 Starting local deployment of Todo Chat Bot..."

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Please start minikube first:"
    echo "   minikube start"
    exit 1
fi

echo "✅ Minikube is running"

# Set Docker environment to use minikube's Docker daemon
echo "🐳 Setting Docker environment to minikube..."
eval $(minikube docker-env)

# Build frontend image
echo "🏗️  Building frontend image..."
cd ../frontend
docker build -t todo-frontend:latest . --no-cache
cd ../..

# Build backend image
echo "🏗️  Building backend image..."
cd ../backend
docker build -t todo-backend:latest . --no-cache
cd ../..

echo "✅ Images built successfully"

# Check if Helm release already exists
if helm status todo-app &> /dev/null; then
    echo "🔄 Updating existing release..."
    helm upgrade todo-app todo-chat-bot -f values-local.yaml
else
    echo "📦 Installing new release..."
    helm install todo-app todo-chat-bot -f values-local.yaml
fi

echo "🎉 Deployment completed!"

echo ""
echo "📱 To access the application:"
echo "   Frontend: $(minikube service todo-chat-bot-frontend --url 2>/dev/null || echo 'kubectl port-forward svc/todo-chat-bot-frontend 3000:3000')"
echo "   Backend:  $(minikube service todo-chat-bot-backend --url 2>/dev/null || echo 'kubectl port-forward svc/todo-chat-bot-backend 7860:7860')"

echo ""
echo "📊 To check status:"
echo "   kubectl get pods"
echo "   kubectl get services"
echo "   kubectl get ingress"

echo ""
echo "🧹 To cleanup:"
echo "   helm uninstall todo-app"