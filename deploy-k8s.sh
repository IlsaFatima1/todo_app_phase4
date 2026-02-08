#!/bin/bash

# Script to deploy the Todo Chatbot application to Minikube

set -e  # Exit on any error

echo "Starting deployment of Todo Chatbot to Minikube..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if minikube is available
if ! command -v minikube &> /dev/null; then
    echo "minikube is not installed. Please install minikube first."
    exit 1
fi

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start
fi

echo "Minikube is running."

# Apply the namespace
echo "Creating namespace..."
kubectl apply -f k8s-manifests/namespace.yaml

# Wait a bit for the namespace to be created
sleep 5

# Apply the database components
echo "Deploying database components..."
kubectl apply -f k8s-manifests/db-pvc.yaml
kubectl apply -f k8s-manifests/db-deployment.yaml

# Apply the configuration
echo "Deploying configuration..."
kubectl apply -f k8s-manifests/configmap.yaml

# Apply the application deployments
echo "Deploying backend..."
kubectl apply -f k8s-manifests/backend-deployment.yaml

echo "Deploying frontend..."
kubectl apply -f k8s-manifests/frontend-deployment.yaml

# Apply scaling and networking configurations
echo "Deploying HPA and network policies..."
kubectl apply -f k8s-manifests/hpa.yaml
kubectl apply -f k8s-manifests/network-policy.yaml

# Enable and apply ingress
echo "Enabling ingress addon and deploying ingress..."
minikube addons enable ingress
kubectl apply -f k8s-manifests/ingress.yaml

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres-db -n todo-chatbot --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n todo-chatbot --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n todo-chatbot --timeout=120s

echo "Deployment completed successfully!"

echo ""
echo "To access the application:"
echo "1. Add to your hosts file: $(minikube ip) todo.local"
echo "2. Access at: http://todo.local"
echo ""
echo "Or use port forwarding:"
echo "kubectl port-forward -n todo-chatbot svc/frontend-service 3000:3000"
echo "kubectl port-forward -n todo-chatbot svc/backend-service 7860:7860"

echo ""
echo "To check status: kubectl get all -n todo-chatbot"