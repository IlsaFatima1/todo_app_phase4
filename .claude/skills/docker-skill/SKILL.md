---
name: docker-fullstack-containerization
description: Containerize frontend and backend applications using Docker. Use for full-stack deployment and development environments.
---

# Docker Full-Stack Containerization

## Instructions

1. **Project structure**
   - Separate frontend and backend folders
   - Include Dockerfile in each service
   - Use docker-compose for orchestration

2. **Container setup**
   - Create lightweight Docker images
   - Configure environment variables
   - Expose required ports
   - Use volumes for development

3. **Service orchestration**
   - Define services in docker-compose.yml
   - Connect services using networks
   - Set dependencies between containers
   - Enable hot reload (if needed)

4. **Build & Run**
   - Build images using Dockerfile
   - Start containers with docker-compose
   - Monitor logs and health status
   - Restart on failure

## Best Practices
- Use multi-stage builds
- Keep images minimal
- Store secrets in .env files
- Avoid hardcoding credentials
- Use .dockerignore
- Version your images
- Document setup steps

## Example Structure
```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    env_file:
      - .env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
