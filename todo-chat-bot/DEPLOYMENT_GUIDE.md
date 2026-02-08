# Local Deployment Guide for Todo Chat Bot

## Overview
This guide will help you deploy the Todo Chat Bot application to your local Minikube cluster using Helm.

## Prerequisites

1. **Minikube** - Running and accessible
   ```bash
   minikube start
   ```

2. **Docker** - For building images
   ```bash
   docker --version
   ```

3. **Helm** - Version 3.0+
   ```bash
   helm version
   ```

4. **kubectl** - Configured to use minikube
   ```bash
   kubectl cluster-info
   ```

## Architecture

The application consists of:
- **Frontend**: Next.js application (Port 3000)
- **Backend**: FastAPI application (Port 7860)

## Step-by-Step Deployment

### Step 1: Configure Minikube Docker Environment

```bash
# On Linux/Mac
eval $(minikube docker-env)

# On Windows PowerShell
& minikube docker-env --shell powershell | Invoke-Expression
```

### Step 2: Build Docker Images

Build both frontend and backend images in Minikube's Docker environment:

```bash
# Build frontend
cd frontend
docker build -t todo-frontend:latest .

# Build backend
cd ../backend
docker build -t todo-backend:latest .
```

### Step 3: Create Kubernetes Secrets (Optional)

If you want to use secrets instead of environment variables:

```bash
kubectl create secret generic db-secret \
  --from-literal=database_url='sqlite:///./todo_app.db'

kubectl create secret generic app-secret \
  --from-literal=secret_key='your-secret-key-here'

kubectl create secret generic gemini-secret \
  --from-literal=api_key='your-gemini-api-key-here'
```

Then update `values-local.yaml` to set `backend.secrets.create: true`

### Step 4: Deploy with Helm

#### Option A: Using the deployment script (Recommended)

**On Linux/Mac:**
```bash
cd todo-chat-bot
chmod +x deploy-local.sh
./deploy-local.sh
```

**On Windows PowerShell:**
```powershell
cd todo-chat-bot
.\deploy-local.ps1
```

#### Option B: Manual Helm installation

```bash
cd todo-chat-bot

# Install
helm install todo-app . -f values-local.yaml

# Or upgrade if already installed
helm upgrade todo-app . -f values-local.yaml
```

### Step 5: Verify Deployment

Check that all pods are running:

```bash
kubectl get pods
kubectl get services
kubectl get deployments
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
todo-chat-bot-backend-xxxxxxxxx-xxxxx   1/1     Running   0          1m
todo-chat-bot-frontend-xxxxxxxxx-xxxxx  1/1     Running   0          1m
```

### Step 6: Access the Application

#### Method 1: Using Minikube Service (Recommended)

```bash
# Access frontend
minikube service todo-chat-bot-frontend --url

# Access backend
minikube service todo-chat-bot-backend --url
```

#### Method 2: Using Port Forwarding

```bash
# Forward frontend
kubectl port-forward svc/todo-chat-bot-frontend 3000:3000

# Forward backend (in another terminal)
kubectl port-forward svc/todo-chat-bot-backend 7860:7860
```

Then access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:7860/docs

#### Method 3: Using Ingress (if enabled)

```bash
# Get minikube IP
minikube ip

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
<minikube-ip> todo.local

# Access at http://todo.local
```

## Troubleshooting

### Pods not starting

```bash
# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

### Image pull errors

Make sure you're using Minikube's Docker daemon:
```bash
eval $(minikube docker-env)
docker images | grep todo
```

You should see your images listed.

### Backend connection issues

Check that the backend service is accessible:
```bash
kubectl get svc todo-chat-bot-backend
kubectl describe svc todo-chat-bot-backend
```

### Database issues

The backend uses SQLite by default. For persistent storage, you may need to add a PersistentVolumeClaim.

## Updating the Application

### Update images and redeploy

```bash
# Rebuild images
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Restart deployments
kubectl rollout restart deployment/todo-chat-bot-frontend
kubectl rollout restart deployment/todo-chat-bot-backend
```

### Update Helm release

```bash
helm upgrade todo-app todo-chat-bot -f values-local.yaml
```

## Cleanup

### Uninstall the application

```bash
helm uninstall todo-app
```

### Delete secrets (if created)

```bash
kubectl delete secret db-secret app-secret gemini-secret
```

### Stop Minikube

```bash
minikube stop
```

## Configuration Options

### values-local.yaml

Key configuration options:

```yaml
frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never  # Use local images
  service:
    type: NodePort     # Expose via NodePort

backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # Use local images
  env:
    - name: DATABASE_URL
      value: "sqlite:///./todo_app_local.db"
    - name: GEMINI_API_KEY
      value: "your-api-key-here"
```

## Common Commands

```bash
# View all resources
kubectl get all

# View logs
kubectl logs -f deployment/todo-chat-bot-frontend
kubectl logs -f deployment/todo-chat-bot-backend

# Execute into pod
kubectl exec -it <pod-name> -- /bin/sh

# View Helm releases
helm list

# View Helm values
helm get values todo-app

# Dry run to see what will be deployed
helm install todo-app todo-chat-bot -f values-local.yaml --dry-run --debug
```

## Next Steps

1. Configure your Gemini API key in `values-local.yaml`
2. Customize resource limits based on your system
3. Set up persistent storage for the database
4. Configure ingress for easier access
5. Add monitoring and logging

## Support

For issues or questions, check:
- Pod logs: `kubectl logs <pod-name>`
- Pod events: `kubectl describe pod <pod-name>`
- Service endpoints: `kubectl get endpoints`