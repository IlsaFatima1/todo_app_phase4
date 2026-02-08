# Kubernetes Deployment for Todo Chatbot

This directory contains Kubernetes manifests for deploying the Todo Chatbot application on a local Minikube cluster.

## Overview

The deployment includes:
- Namespace: `todo-chatbot`
- Database: PostgreSQL with persistent storage
- Backend: FastAPI application
- Frontend: Next.js application
- Services for internal and external communication
- Ingress for external access
- Horizontal Pod Autoscalers for scaling
- Network policies for security
- ConfigMaps for configuration

## Prerequisites

- Minikube installed and running
- kubectl installed and configured
- kubectl-ai (optional) for AI-assisted operations

## Deployment Steps

1. **Start Minikube** (if not already running):
   ```bash
   minikube start
   ```

2. **Apply the namespace**:
   ```bash
   kubectl apply -f namespace.yaml
   ```

3. **Apply the database components**:
   ```bash
   kubectl apply -f db-pvc.yaml
   kubectl apply -f db-deployment.yaml
   ```

4. **Apply the configuration**:
   ```bash
   kubectl apply -f configmap.yaml
   ```

5. **Apply the application deployments**:
   ```bash
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f frontend-deployment.yaml
   ```

6. **Apply the scaling and networking configurations**:
   ```bash
   kubectl apply -f hpa.yaml
   kubectl apply -f network-policy.yaml
   ```

7. **Apply the ingress** (after enabling ingress addon):
   ```bash
   minikube addons enable ingress
   kubectl apply -f ingress.yaml
   ```

## Accessing the Application

After deployment, you can access the application in one of the following ways:

1. **Using Ingress** (recommended):
   - Add the following line to your hosts file (`/etc/hosts` on Linux/Mac, `C:\Windows\System32\drivers\etc\hosts` on Windows):
     ```
     <minikube-ip> todo.local
     ```
   - Find the Minikube IP with `minikube ip`
   - Access the application at: http://todo.local

2. **Using port forwarding**:
   ```bash
   kubectl port-forward -n todo-chatbot svc/frontend-service 3000:3000
   kubectl port-forward -n todo-chatbot svc/backend-service 7860:7860
   ```

## AI-Assisted Management

Use kubectl-ai for AI-assisted cluster management:

```bash
kubectl ai "Show me the status of all pods in the todo-chatbot namespace"
kubectl ai "Why is my backend pod not starting?"
kubectl ai "Recommend resource optimizations for the backend deployment"
```

## Verification

To verify the deployment:

```bash
# Check all resources
kubectl get all -n todo-chatbot

# Check ingress
kubectl get ingress -n todo-chatbot

# Check pod statuses
kubectl get pods -n todo-chatbot

# Check logs for any component
kubectl logs -n todo-chatbot deployment/backend
```

## Troubleshooting

- If pods are not starting, check the logs: `kubectl logs -n todo-chatbot <pod-name>`
- If services are not accessible, verify network policies are not blocking traffic
- If database is not connecting, ensure the backend has the correct database service name
- For scaling issues, check HPA status: `kubectl get hpa -n todo-chatbot`

## Cleanup

To remove the entire deployment:

```bash
kubectl delete namespace todo-chatbot
```