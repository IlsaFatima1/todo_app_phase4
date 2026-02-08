# Helm Chart Update Summary

## Overview
The Todo Chat Bot Helm chart has been updated for local deployment with Minikube. The chart now supports deploying both frontend (Next.js) and backend (FastAPI) services.

## Files Updated

### 1. Chart.yaml
- Updated description to reflect Todo Chat Bot application
- Bumped version to 0.2.0
- Updated appVersion to 1.0.0

### 2. values.yaml
**Major Changes:**
- Split configuration into `frontend` and `backend` sections
- Added enable/disable flags for each service
- Configured separate image repositories and tags
- Set up environment variables for both services
- Added secrets configuration for backend
- Updated ingress to use localhost
- Changed default service type to ClusterIP

**Frontend Configuration:**
```yaml
frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: frontend-app
    tag: "local"
  service:
    type: ClusterIP
    port: 3000
```

**Backend Configuration:**
```yaml
backend:
  enabled: true
  replicaCount: 1
  image:
    repository: backend-app
    tag: "local"
  service:
    type: ClusterIP
    port: 7860
  env:
    - DATABASE_URL (from secret)
    - SECRET_KEY (from secret)
    - GEMINI_API_KEY (from secret)
```

### 3. templates/deployment.yaml
**Major Changes:**
- Split into two separate deployments: frontend and backend
- Each deployment has its own selector labels
- Frontend uses port 3000, backend uses port 7860
- Backend includes health check probes pointing to /docs endpoint
- Both deployments support conditional rendering based on enabled flag

### 4. templates/service.yaml
**Major Changes:**
- Split into two separate services
- Frontend service: `todo-chat-bot-frontend` on port 3000
- Backend service: `todo-chat-bot-backend` on port 7860
- Each service has proper app labels for pod selection

### 5. templates/ingress.yaml
**Major Changes:**
- Routes traffic to frontend service
- Updated to use `todo-chat-bot-frontend` service name
- Default host set to `localhost`

### 6. templates/httproute.yaml
**Major Changes:**
- Routes traffic to frontend service
- Updated backend reference to use frontend service

## New Files Created

### 1. templates/secrets.yaml
Creates three Kubernetes secrets for backend:
- `db-secret`: Database connection string
- `app-secret`: Application secret key
- `gemini-secret`: Gemini API key

### 2. templates/configmap.yaml
Creates ConfigMaps for both services:
- Frontend config: API URL configuration
- Backend config: Logging and debug settings

### 3. values-local.yaml
Local development overrides:
- Image pull policy set to `Never` (use local images)
- Service type set to `NodePort` for easy access
- Direct environment variable configuration (no secrets)
- Resource limits suitable for local development

### 4. README.md
Basic Helm chart documentation including:
- Installation instructions
- Configuration parameters
- Uninstallation steps
- Minikube-specific guidance

### 5. DEPLOYMENT_GUIDE.md
Comprehensive deployment guide with:
- Prerequisites checklist
- Step-by-step deployment instructions
- Multiple access methods
- Troubleshooting section
- Common commands reference

### 6. deploy-local.sh (Bash)
Automated deployment script for Linux/Mac:
- Checks Minikube status
- Builds Docker images
- Installs/upgrades Helm release
- Provides access URLs

### 7. deploy-local.ps1 (PowerShell)
Automated deployment script for Windows:
- Same functionality as bash script
- Windows-compatible commands
- Colored output for better UX

### 8. validate.sh (Bash)
Pre-deployment validation script:
- Checks required tools
- Validates Minikube status
- Lints Helm chart
- Tests template rendering

### 9. validate.ps1 (PowerShell)
Windows version of validation script:
- Same checks as bash version
- PowerShell-native commands

## Key Features

### Multi-Service Architecture
- Separate deployments for frontend and backend
- Independent scaling and configuration
- Proper service discovery via Kubernetes DNS

### Local Development Optimized
- Uses local Docker images (no registry needed)
- NodePort services for easy access
- Simplified configuration
- Fast iteration cycle

### Flexible Configuration
- Enable/disable services independently
- Override any value via values files
- Support for both secrets and direct env vars
- Resource limits configurable

### Production Ready Structure
- Proper health checks
- ConfigMaps for configuration
- Secrets for sensitive data
- Service accounts
- Ingress support

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│           Minikube Cluster              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │         Ingress (Optional)       │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │   Frontend Service (NodePort)    │  │
│  │         Port: 3000               │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │   Frontend Deployment            │  │
│  │   Image: todo-frontend:latest    │  │
│  │   Replicas: 1                    │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Backend Service (NodePort)     │  │
│  │         Port: 7860               │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │   Backend Deployment             │  │
│  │   Image: todo-backend:latest     │  │
│  │   Replicas: 1                    │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Secrets & ConfigMaps           │  │
│  │   - db-secret                    │  │
│  │   - app-secret                   │  │
│  │   - gemini-secret                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Next Steps

1. **Validate Prerequisites**
   ```bash
   # Linux/Mac
   ./validate.sh

   # Windows
   .\validate.ps1
   ```

2. **Update Configuration**
   - Edit `values-local.yaml`
   - Set your Gemini API key
   - Adjust resource limits if needed

3. **Deploy Application**
   ```bash
   # Linux/Mac
   ./deploy-local.sh

   # Windows
   .\deploy-local.ps1
   ```

4. **Access Application**
   ```bash
   minikube service todo-chat-bot-frontend --url
   minikube service todo-chat-bot-backend --url
   ```

## Troubleshooting

See DEPLOYMENT_GUIDE.md for detailed troubleshooting steps.

## Configuration Reference

### Image Configuration
- `frontend.image.repository`: Frontend Docker image name
- `frontend.image.tag`: Frontend image tag
- `backend.image.repository`: Backend Docker image name
- `backend.image.tag`: Backend image tag

### Service Configuration
- `frontend.service.type`: Service type (ClusterIP/NodePort/LoadBalancer)
- `frontend.service.port`: Frontend service port
- `backend.service.type`: Service type
- `backend.service.port`: Backend service port

### Environment Variables
- `BACKEND_URL`: Backend service URL for frontend
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key
- `GEMINI_API_KEY`: Gemini API key

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name>`
2. Describe resources: `kubectl describe <resource-type> <resource-name>`
3. Review DEPLOYMENT_GUIDE.md
4. Check Helm values: `helm get values todo-app`