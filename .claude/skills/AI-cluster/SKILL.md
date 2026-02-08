---
name: ai-cluster-optimization
description: Continuously monitor and optimize Docker and Kubernetes clusters using kubectl-ai and Kagent for intelligent automation.
---

# AI-Driven Cluster Monitoring & Optimization

## Instructions

1. **Monitoring setup**
   - Enable Kubernetes metrics server
   - Configure Docker and container logs
   - Integrate Prometheus and Grafana
   - Collect system and pod metrics

2. **AI integration**
   - Install kubectl-ai
   - Configure API credentials
   - Connect to active clusters
   - Enable natural language queries

3. **Agent configuration**
   - Deploy Kagent
   - Set monitoring permissions (RBAC)
   - Configure alert policies
   - Enable auto-remediation rules

4. **Performance optimization**
   - Analyze CPU and memory usage
   - Detect bottlenecks and crashes
   - Optimize container images
   - Tune resource requests and limits

5. **Automation workflows**
   - Enable auto-scaling policies
   - Automate pod restarts
   - Trigger rollbacks on failures
   - Schedule maintenance tasks

## Best Practices
- Define clear SLOs and SLAs
- Use resource quotas per namespace
- Secure AI access tokens
- Monitor anomaly patterns
- Keep agents updated
- Audit automation actions
- Test optimization rules regularly

## Example Structure
```bash
# Enable metrics
minikube addons enable metrics-server

# Install kubectl-ai
kubectl ai install

# Deploy Kagent
kubectl apply -f kagent.yaml

# Check resource usage
kubectl top pods
kubectl top nodes

# AI-assisted analysis
kubectl ai "Which pods are consuming the most memory?"

# Auto-scale deployment
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10
