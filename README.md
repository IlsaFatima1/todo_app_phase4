# Containerization of Cloud-Native Todo Chatbot

This project demonstrates containerization of the Todo Chatbot application using Docker and Docker Compose, with AI-assisted optimization capabilities.

## Overview

The application consists of:
- Frontend: Next.js 14 application
- Backend: FastAPI application with SQLModel
- Database: PostgreSQL

## Prerequisites

- Docker Desktop 4.53+
- Docker Compose v2.20+

## Quick Start

1. Build and start the services:
   ```bash
   docker-compose up --build
   ```

2. The application will be available at: http://localhost:7860

## Docker Images

### Backend (Primary Service)
- Built with multi-stage build for optimization
- Runs as non-root user for security
- Includes health checks
- Serves both API and frontend assets

### Database
- PostgreSQL 15 for data persistence
- Automatic initialization with init.sql

## Security Features

- Non-root users in containers
- Minimal base images
- Health checks for all services
- Isolated networks

## Gordon AI Integration

For AI-assisted optimization, install Gordon and run:
```bash
gordon analyze backend/Dockerfile
```

Follow the recommendations to further optimize your container images.

## Build Optimization

- Multi-stage builds to reduce image size
- Layer caching for faster builds
- .dockerignore files for clean builds