---
name: local-k8s-ai-environment
description: Set up a local Kubernetes environment using Minikube, kubectl-ai, and Kagent for AI-assisted cluster management and development.
---

# Local Kubernetes AI-Ready Environment

## Instructions

1. **Environment setup**
   - Install Minikube and kubectl
   - Enable virtualization (Docker/Hyper-V/VM)
   - Configure system resources
   - Verify cluster status

2. **Cluster initialization**
   - Start Minikube with required drivers
   - Configure CPU and memory
   - Enable essential addons
   - Set default namespace

3. **AI-assisted management**
   - Install kubectl-ai
   - Configure API keys
   - Integrate with kubectl
   - Use natural language commands

4. **Agent deployment**
   - Install Kagent
   - Configure permissions (RBAC)
   - Connect to cluster context
   - Enable monitoring features

5. **Application deployment**
   - Deploy sample workloads
   - Expose services locally
   - Test connectivity
   - Validate scaling

## Best Practices
- Allocate sufficient memory and CPU
- Use namespaces for isolation
- Secure API credentials
- Regularly update tools
- Enable autoscaling for testing
- Backup cluster configs
- Monitor resource usage

## Example Structure
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Install kubectl-ai
kubectl ai install

# Verify cluster
kubectl get nodes

# Deploy sample app
kubectl create deployment demo-app --image=nginx
kubectl expose deployment demo-app --type=NodePort --port=80
