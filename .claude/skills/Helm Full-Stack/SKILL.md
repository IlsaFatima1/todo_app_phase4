---
name: helm-fullstack-ai-deployment
description: Create and manage Helm charts for frontend and backend applications using kubectl-ai for intelligent Kubernetes deployments.
---

# Helm Full-Stack AI Deployment

## Instructions

1. **Project structure**
   - Create separate Helm charts for frontend and backend
   - Organize templates, values, and charts
   - Follow Helm naming conventions
   - Maintain version control

2. **Chart development**
   - Generate base charts using Helm CLI
   - Configure Deployment, Service, and Ingress templates
   - Parameterize images, ports, and resources
   - Define environment variables

3. **AI-assisted configuration**
   - Install kubectl-ai
   - Connect to cluster context
   - Use natural language for YAML generation
   - Validate manifests automatically

4. **Packaging & deployment**
   - Package Helm charts
   - Install and upgrade releases
   - Roll back on failures
   - Manage release versions

5. **Testing & validation**
   - Run Helm lint checks
   - Perform dry runs
   - Verify pod health
   - Monitor rollout status

## Best Practices
- Use reusable templates
- Keep values.yaml clean
- Avoid hardcoding secrets
- Apply semantic versioning
- Document chart usage
- Enable resource limits
- Test upgrades regularly

## Example Structure
```bash
# Create charts
helm create frontend
helm create backend

# Lint charts
helm lint frontend
helm lint backend

# Install releases
helm install frontend-app ./frontend
helm install backend-app ./backend

# Upgrade with new values
helm upgrade frontend-app ./frontend -f values-prod.yaml

# AI-assisted troubleshooting
kubectl ai "Why is my frontend pod crashing?"
