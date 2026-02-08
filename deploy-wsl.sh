#!/bin/bash
set -e

echo "🚀 Starting deployment in WSL..."

# Navigate to project directory
cd /mnt/d/gemini_cli/hackathon2

# Set Docker environment to use minikube
eval $(minikube -p minikube docker-env)

echo "📦 Checking for existing images..."
docker images | grep -E "todo-frontend|todo-backend" || echo "No images found yet"

echo "🏗️  Building frontend image..."
docker build -t todo-frontend:latest ./frontend

echo "🏗️  Building backend image..."
docker build -t todo-backend:latest ./backend

echo "✅ Images built successfully"

echo "📦 Deploying with Helm..."
cd todo-chat-bot

# Check if release exists
if helm status todo-app &> /dev/null; then
    echo "🔄 Upgrading existing release..."
    helm upgrade todo-app . -f values-local.yaml
else
    echo "📦 Installing new release..."
    helm install todo-app . -f values-local.yaml
fi

echo "✅ Deployment completed!"

echo ""
echo "📊 Checking deployment status..."
kubectl get pods
kubectl get services

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "To access the application, run:"
echo "  minikube service todo-chat-bot-frontend --url"
echo "  minikube service todo-chat-bot-backend --url"
