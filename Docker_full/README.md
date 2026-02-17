# Docker Complete Guide

This folder contains comprehensive Docker documentation, examples, and best practices covering all aspects of Docker containerization.

## 📁 Folder Contents

### 1. **01-basic-dockerfile**

Basic Dockerfile examples for popular programming languages and frameworks:

- Python applications
- Node.js applications
- Java Spring Boot applications
- Go applications
- .NET Core applications

**Use Case:** Quick-start templates for containerizing your applications.

### 2. **02-multistage-dockerfile**

Advanced multi-stage build examples:

- Testing and security scanning stages
- Build optimization
- Development vs Production configurations
- Full-stack applications
- Microservices with multiple binaries

**Use Case:** Production-ready, optimized Docker images with minimal size and security scanning.

### 3. **03-docker-compose.yml**

Complete Docker Compose configuration featuring:

- Frontend service (React/Vue/Angular)
- Backend API service
- PostgreSQL, MongoDB, Redis databases
- RabbitMQ message queue
- Elasticsearch search engine
- Nginx reverse proxy
- Worker services
- Monitoring stack (Prometheus + Grafana)
- Distributed tracing (Jaeger)

**Use Case:** Full-stack application deployment with all supporting services.

### 4. **04-dockerignore**

Comprehensive .dockerignore file to exclude:

- Development files
- IDE configurations
- Dependencies (install fresh in container)
- Test files
- Logs and temporary files
- Sensitive data

**Use Case:** Reduce build context size and improve security by excluding unnecessary files.

### 5. **05-docker-security-best-practices**

Security-hardened Dockerfile examples:

- Non-root user configuration
- Minimal base images (distroless, alpine, scratch)
- Read-only filesystems
- Security scanning integration
- Secrets management
- HIPAA-compliant configurations
- Capability dropping
- Resource limits

**Use Case:** Production deployments requiring high security standards.

### 6. **06-docker-networking**

Network configuration examples:

- Bridge networks (default)
- Host networks
- Overlay networks (multi-host)
- Macvlan networks
- Custom network configurations
- DNS configuration
- Service discovery
- Network isolation and policies
- Load balancing
- IPv6 support

**Use Case:** Understanding and configuring container networking for various scenarios.

### 7. **07-docker-volumes**

Volume management examples:

- Named volumes (recommended)
- Bind mounts
- Tmpfs mounts (in-memory)
- Volume drivers (NFS, CIFS, cloud)
- Database persistent storage
- Backup and restore
- Shared volumes
- Volume permissions
- Volume plugins

**Use Case:** Data persistence, sharing data between containers, and backup strategies.

### 8. **08-docker-commands-cheatsheet.md**

Complete command reference:

- Container management (run, stop, start, remove)
- Image operations (build, push, pull, tag)
- Volume commands
- Network commands
- Docker Compose commands
- System management
- Registry operations
- Docker Swarm
- Security scanning
- Troubleshooting commands

**Use Case:** Quick reference for all Docker CLI commands.

### 9. **09-real-world-examples.yml**

Production-ready Docker Compose examples:

1. **WordPress + MySQL** - Blog/CMS platform
2. **MERN Stack** - MongoDB, Express, React, Node.js
3. **Microservices E-Commerce** - Complete e-commerce platform with multiple services
4. **CI/CD Pipeline** - Jenkins, SonarQube, Nexus
5. **ELK Stack** - Elasticsearch, Logstash, Kibana for logging
6. **Monitoring Stack** - Prometheus, Grafana, Alertmanager

**Use Case:** Reference architectures for common application stacks.

### 10. **10-docker-troubleshooting.md**

Comprehensive troubleshooting guide:

- Container startup issues
- Image build failures
- Performance problems (CPU, Memory, Disk)
- Network connectivity issues
- Volume and permission problems
- Docker Compose issues
- Security concerns
- Logging problems
- Docker Desktop (Windows) specific issues
- Debugging tools and techniques

**Use Case:** Diagnose and fix common Docker problems.

---

## 🚀 Quick Start

### 1. Basic Application Containerization

```bash
# Choose appropriate Dockerfile from 01-basic-dockerfile
# Example for Node.js app:
cd your-nodejs-project
docker build -t myapp:latest .
docker run -d -p 3000:3000 --name myapp myapp:latest
```

### 2. Development Environment with Docker Compose

```bash
# Use 03-docker-compose.yml as template
docker-compose up -d
docker-compose logs -f
```

### 3. Production Deployment

```bash
# Use security-hardened Dockerfile from 05-docker-security-best-practices
docker build -t myapp:prod -f Dockerfile.prod .
docker run -d \
  --name myapp \
  --read-only \
  --user 1000:1000 \
  --cap-drop ALL \
  -p 8080:8080 \
  myapp:prod
```

---

## 📋 Best Practices Checklist

### Security

- ✅ Use specific image versions (not `latest`)
- ✅ Run containers as non-root user
- ✅ Use minimal base images (Alpine, distroless)
- ✅ Scan images for vulnerabilities
- ✅ Don't include secrets in images
- ✅ Use read-only filesystems where possible
- ✅ Drop unnecessary capabilities
- ✅ Set resource limits

### Performance

- ✅ Use multi-stage builds
- ✅ Minimize layer count
- ✅ Leverage build cache
- ✅ Use .dockerignore
- ✅ Set appropriate resource limits
- ✅ Use health checks
- ✅ Implement proper logging

### Maintainability

- ✅ Use docker-compose for local development
- ✅ Document Dockerfile with comments
- ✅ Use environment variables for configuration
- ✅ Implement proper health checks
- ✅ Use named volumes for data persistence
- ✅ Tag images with semantic versions
- ✅ Keep images up to date

---

## 🛠️ Common Commands

### Container Lifecycle

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d --name myapp -p 8080:80 myapp:latest

# View logs
docker logs -f myapp

# Execute command
docker exec -it myapp bash

# Stop container
docker stop myapp

# Remove container
docker rm myapp
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Scale services
docker-compose up -d --scale app=3
```

### Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```

---

## 📚 Learning Path

### Beginner

1. Read `01-basic-dockerfile` - Understand Dockerfile basics
2. Practice `08-docker-commands-cheatsheet.md` - Learn essential commands
3. Try `09-real-world-examples.yml` - WordPress example

### Intermediate

1. Study `02-multistage-dockerfile` - Multi-stage builds
2. Explore `03-docker-compose.yml` - Full-stack applications
3. Learn `06-docker-networking` - Network configurations
4. Practice `07-docker-volumes` - Data persistence

### Advanced

1. Master `05-docker-security-best-practices` - Security hardening
2. Implement `09-real-world-examples.yml` - Microservices architecture
3. Study `10-docker-troubleshooting.md` - Problem diagnosis
4. Optimize builds and deployments

---

## 🔧 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs container_name

# Check exit code
docker inspect --format='{{.State.ExitCode}}' container_name

# Run interactively
docker run -it --entrypoint /bin/bash image_name
```

### Build failures

```bash
# Build without cache
docker build --no-cache -t myapp .

# Use BuildKit
$env:DOCKER_BUILDKIT=1
docker build -t myapp .
```

### Network issues

```bash
# Check network
docker network inspect bridge

# Test connectivity
docker exec container1 ping container2
```

For detailed troubleshooting, see `10-docker-troubleshooting.md`.

---

## 🌟 Real-World Use Cases

### 1. Development Environment

Use `03-docker-compose.yml` to create consistent development environments across team members.

### 2. CI/CD Pipeline

Implement `09-real-world-examples.yml` (Jenkins + SonarQube) for automated testing and deployment.

### 3. Microservices Architecture

Deploy `09-real-world-examples.yml` (E-Commerce) for scalable microservices.

### 4. Monitoring & Logging

Set up `09-real-world-examples.yml` (ELK Stack or Prometheus) for observability.

### 5. Production Deployment

Use security-hardened Dockerfiles from `05-docker-security-best-practices`.

---

## 📖 Additional Resources

### Official Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)

### Best Practices

- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)

### Tools

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Trivy](https://github.com/aquasecurity/trivy) - Security scanner
- [Dive](https://github.com/wagoodman/dive) - Image layer analyzer
- [Hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter

---

## 🤝 Contributing

Feel free to add more examples or improve existing ones. Follow these guidelines:

1. Keep examples clear and well-commented
2. Include use cases and explanations
3. Follow Docker best practices
4. Test all examples before committing

---

## 📝 License

This documentation is for educational purposes. Feel free to use and modify for your projects.

---

## 💡 Tips

1. **Always use .dockerignore** to reduce build context size
2. **Use multi-stage builds** for smaller production images
3. **Run as non-root user** for better security
4. **Set resource limits** to prevent resource exhaustion
5. **Use health checks** for better orchestration
6. **Keep images updated** to get security patches
7. **Use named volumes** instead of bind mounts in production
8. **Log to stdout/stderr** for better log aggregation
9. **Use environment variables** for configuration
10. **Tag images properly** for version tracking

---

## 🔍 Quick Reference

### File Purpose Summary

| File                              | Purpose                     | When to Use               |
| --------------------------------- | --------------------------- | ------------------------- |
| 01-basic-dockerfile               | Simple Dockerfile templates | Starting new project      |
| 02-multistage-dockerfile          | Optimized production builds | Production deployment     |
| 03-docker-compose.yml             | Full-stack application      | Development environment   |
| 04-dockerignore                   | Exclude files from build    | Every project             |
| 05-docker-security-best-practices | Security-hardened configs   | Production/Compliance     |
| 06-docker-networking              | Network configurations      | Multi-container apps      |
| 07-docker-volumes                 | Data persistence            | Stateful applications     |
| 08-docker-commands-cheatsheet.md  | CLI reference               | Daily operations          |
| 09-real-world-examples.yml        | Production architectures    | Reference implementations |
| 10-docker-troubleshooting.md      | Problem solving             | When things break         |

---

**Happy Dockerizing! 🐳**
