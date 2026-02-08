# Todo Chat Bot Helm Chart

This Helm chart deploys the Todo Chat Bot application, which consists of:
- Frontend: Next.js application
- Backend: FastAPI application

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube or a Kubernetes cluster for local deployment

## Installation

### Local Development

1. Build your frontend and backend Docker images:
   ```bash
   # Build frontend image
   cd frontend
   docker build -t todo-frontend:latest .

   # Build backend image
   cd ../backend
   docker build -t todo-backend:latest .
   ```

2. Install the chart with local values:
   ```bash
   # For Minikube, make sure Docker images are available in minikube
   eval $(minikube docker-env)

   # Install the chart
   helm install todo-app todo-chat-bot -f values-local.yaml
   ```

### Quick Install (Development)

```bash
helm install todo-app todo-chat-bot --set frontend.image.pullPolicy=Never --set backend.image.pullPolicy=Never
```

## Configuration

The following table lists the configurable parameters of the todo-chat-bot chart and their default values.

### Frontend Parameters

| Parameter                     | Description                                      | Default                          |
|-------------------------------|--------------------------------------------------|----------------------------------|
| `frontend.enabled`           | Enable frontend deployment                       | `true`                          |
| `frontend.replicaCount`      | Number of frontend replicas                      | `1`                             |
| `frontend.image.repository`  | Frontend image repository                        | `todo-frontend`                 |
| `frontend.image.pullPolicy`  | Frontend image pull policy                       | `IfNotPresent`                  |
| `frontend.image.tag`         | Frontend image tag                               | `""`                            |
| `frontend.service.type`      | Frontend service type                            | `ClusterIP`                     |
| `frontend.service.port`      | Frontend service port                            | `3000`                          |

### Backend Parameters

| Parameter                    | Description                                       | Default                         |
|------------------------------|---------------------------------------------------|---------------------------------|
| `backend.enabled`           | Enable backend deployment                         | `true`                         |
| `backend.replicaCount`      | Number of backend replicas                        | `1`                            |
| `backend.image.repository`  | Backend image repository                          | `todo-backend`                 |
| `backend.image.pullPolicy`  | Backend image pull policy                         | `IfNotPresent`                 |
| `backend.image.tag`         | Backend image tag                                 | `""`                           |
| `backend.service.type`      | Backend service type                              | `ClusterIP`                    |
| `backend.service.port`      | Backend service port                              | `7860`                         |

## Uninstalling the Chart

To uninstall/delete the `todo-app` release:

```bash
helm delete todo-app
```

## Local Development with Minikube

For local development with Minikube:

1. Start Minikube:
   ```bash
   minikube start
   ```

2. Configure Docker to use Minikube's Docker daemon:
   ```bash
   eval $(minikube docker-env)
   ```

3. Build your images locally:
   ```bash
   docker build -t todo-frontend:latest -f ../frontend/Dockerfile ../frontend
   docker build -t todo-backend:latest -f ../backend/Dockerfile ../backend
   ```

4. Deploy with the local values:
   ```bash
   helm install todo-app todo-chat-bot -f values-local.yaml
   ```

5. Access the application:
   ```bash
   minikube service todo-chat-bot-frontend --url
   ```