# Docker Troubleshooting Guide

## Common Issues and Solutions

### 1. Container Won't Start

#### Issue: Container exits immediately

```bash
# Check container logs
docker logs container_name

# Check container exit code
docker inspect --format='{{.State.ExitCode}}' container_name

# Common exit codes:
# 0   - Success
# 1   - Application error
# 125 - Docker daemon error
# 126 - Command cannot be invoked
# 127 - Command not found
# 137 - Killed (OOM or SIGKILL)
# 139 - Segmentation fault
# 143 - Graceful termination (SIGTERM)

# Solutions:
# 1. Check if entrypoint/command is valid
docker inspect --format='{{.Config.Entrypoint}}' container_name
docker inspect --format='{{.Config.Cmd}}' container_name

# 2. Run container interactively to debug
docker run -it --entrypoint /bin/bash image_name

# 3. Check for missing dependencies
docker run -it image_name sh -c "command -v your_binary"
```

#### Issue: Port already in use

```bash
# Find what's using the port
# Windows PowerShell:
Get-NetTCPConnection -LocalPort 8080 | Select-Object -Property LocalAddress, LocalPort, OwningProcess

# Check process
Get-Process -Id <PID>

# Solutions:
# 1. Use different port
docker run -p 8081:80 nginx

# 2. Stop conflicting service
Stop-Process -Id <PID>

# 3. Remove container using the port
docker ps -a
docker rm -f container_name
```

### 2. Image Build Failures

#### Issue: Build context too large

```bash
# Check build context size
docker build --no-cache .

# Solutions:
# 1. Add .dockerignore file
cat > .dockerignore <<EOF
node_modules/
.git/
*.log
EOF

# 2. Use specific build context
docker build -f Dockerfile -t myapp ./specific-folder

# 3. Use multi-stage builds to reduce final image size
```

#### Issue: Layer caching issues

```bash
# Build without cache
docker build --no-cache -t myapp .

# Pull cache from registry
docker build --cache-from myrepo/myapp:latest -t myapp .

# Use BuildKit for better caching
$env:DOCKER_BUILDKIT=1
docker build -t myapp .
```

#### Issue: Dependency installation fails

```bash
# Common errors and solutions:

# Network issues
docker build --network=host -t myapp .

# DNS issues
docker build --add-host=registry.npmjs.org:104.16.24.35 -t myapp .

# Certificate issues
# Add to Dockerfile:
RUN apt-get update && apt-get install -y ca-certificates

# Timeout issues
# Increase timeout in package manager:
RUN npm config set fetch-timeout 600000
RUN pip install --timeout 300 -r requirements.txt
```

### 3. Container Performance Issues

#### Issue: High CPU usage

```bash
# Check container stats
docker stats container_name

# Limit CPU usage
docker run -d --cpus="1.5" myapp

# Set CPU shares (relative weight)
docker run -d --cpu-shares=512 myapp

# Check processes inside container
docker top container_name
```

#### Issue: High memory usage

```bash
# Check memory usage
docker stats --no-stream container_name

# Limit memory
docker run -d --memory="512m" --memory-swap="1g" myapp

# Check for memory leaks
docker exec container_name ps aux --sort=-%mem | head -10

# View memory details
docker inspect --format='{{.HostConfig.Memory}}' container_name
```

#### Issue: Disk space issues

```bash
# Check disk usage
docker system df

# Detailed view
docker system df -v

# Clean up
docker system prune -a --volumes

# Remove specific items
docker container prune
docker image prune -a
docker volume prune
docker network prune
```

### 4. Network Issues

#### Issue: Container can't reach other containers

```bash
# Check network
docker network ls
docker network inspect bridge

# Check container network settings
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name

# Test connectivity
docker exec container1 ping container2
docker exec container1 nc -zv container2 port

# Solutions:
# 1. Use custom network
docker network create mynetwork
docker run --network mynetwork --name container1 myapp
docker run --network mynetwork --name container2 myapp

# 2. Check DNS resolution
docker exec container1 nslookup container2

# 3. Use explicit links (deprecated but works)
docker run --link container1:alias container2
```

#### Issue: Cannot access container from host

```bash
# Check port mapping
docker port container_name

# Check if container is listening
docker exec container_name netstat -tulpn

# Solutions:
# 1. Verify port mapping
docker run -p 8080:80 nginx

# 2. Bind to all interfaces
docker run -p 0.0.0.0:8080:80 nginx

# 3. Check firewall
# Windows Firewall - ensure Docker is allowed
```

#### Issue: DNS resolution fails

```bash
# Check DNS settings
docker inspect --format='{{.HostConfig.Dns}}' container_name

# Set custom DNS
docker run --dns 8.8.8.8 --dns 8.8.4.4 myapp

# In docker-compose.yml:
services:
  app:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

### 5. Volume Issues

#### Issue: Permission denied on volume

```bash
# Check volume ownership
docker exec container_name ls -la /data

# Solutions:
# 1. Fix permissions before copying
RUN mkdir -p /data && chown -R 1000:1000 /data

# 2. Run as specific user
docker run -u 1000:1000 -v myvolume:/data myapp

# 3. Initialize volume with correct permissions
docker run --rm -v myvolume:/data alpine chown -R 1000:1000 /data
```

#### Issue: Volume data not persisting

```bash
# Check if volume is anonymous
docker volume ls

# Use named volume
docker run -v myvolume:/data myapp

# Inspect volume
docker volume inspect myvolume

# Backup volume
docker run --rm -v myvolume:/data -v ${PWD}:/backup alpine tar czf /backup/backup.tar.gz -C /data .
```

#### Issue: Volume mount not working

```bash
# Windows specific - ensure path is correct
# Use forward slashes or escaped backslashes
docker run -v C:/Users/name/project:/app myapp

# Check if file sharing is enabled in Docker Desktop
# Settings -> Resources -> File Sharing

# Use absolute paths
docker run -v "$(pwd):/app" myapp
```

### 6. Docker Compose Issues

#### Issue: Service dependency not working

```bash
# Use depends_on with condition
services:
  app:
    depends_on:
      db:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

# Use wait-for script
COPY wait-for-it.sh /wait-for-it.sh
CMD ["/wait-for-it.sh", "db:5432", "--", "node", "server.js"]
```

#### Issue: Environment variables not loading

```bash
# Check if .env file exists
cat .env

# Verify variables are loaded
docker-compose config

# Use env_file
services:
  app:
    env_file:
      - .env
      - .env.local
```

#### Issue: Compose file validation errors

```bash
# Validate compose file
docker-compose config

# Check for syntax errors
docker-compose -f docker-compose.yml config

# Use specific compose file version
version: '3.9'
```

### 7. Security Issues

#### Issue: Container running as root

```bash
# Check user
docker exec container_name whoami

# Solution: Run as non-root user
FROM node:18-alpine
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
USER appuser
```

#### Issue: Exposed sensitive data

```bash
# Never do this:
ENV PASSWORD=secret123

# Use Docker secrets
echo "secret123" | docker secret create db_password -

# Or environment variables at runtime
docker run -e PASSWORD=$PASSWORD myapp
```

#### Issue: Vulnerable base image

```bash
# Scan image
docker scan myapp:latest

# Use specific versions
FROM node:18.19.0-alpine3.19

# Use minimal base images
FROM alpine:3.19
FROM distroless/static
FROM scratch
```

### 8. Logging Issues

#### Issue: Logs filling up disk

```bash
# Set log limits in daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Per container
docker run --log-opt max-size=10m --log-opt max-file=3 myapp

# In docker-compose.yml:
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

#### Issue: Cannot view logs

```bash
# Check log driver
docker inspect --format='{{.HostConfig.LogConfig.Type}}' container_name

# If using non-default driver, logs may not be available via docker logs

# Solutions:
# 1. Check log files directly
docker inspect --format='{{.LogPath}}' container_name

# 2. Use log aggregation (ELK, Fluentd)
# 3. Change log driver to json-file
```

### 9. Docker Desktop Issues (Windows)

#### Issue: Docker Desktop won't start

```powershell
# Restart Docker Desktop
Stop-Service docker
Start-Service docker

# Reset Docker Desktop
# Settings -> Troubleshoot -> Reset to factory defaults

# Check Windows features
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# WSL2 backend issues
wsl --status
wsl --update
```

#### Issue: Performance issues on Windows

```bash
# Use WSL2 backend (Settings -> General -> Use WSL2 based engine)

# Allocate more resources
# Settings -> Resources -> Advanced

# Exclude Docker data from antivirus
# Add C:\ProgramData\Docker to exclusions

# Use volume mounts instead of bind mounts for better performance
```

### 10. Debugging Tools

```bash
# Interactive shell
docker exec -it container_name sh

# Network debugging
docker run --rm --network container:myapp nicolaka/netshoot

# Process debugging
docker top container_name

# File system changes
docker diff container_name

# Export container filesystem
docker export container_name -o container.tar

# View real-time events
docker events --filter container=container_name

# Health check status
docker inspect --format='{{.State.Health.Status}}' container_name

# Complete container state
docker inspect container_name | ConvertFrom-Json

# Resource usage over time
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Emergency Recovery

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Complete cleanup
docker system prune -a --volumes -f

# Reset Docker Desktop (Windows)
# Uninstall and reinstall Docker Desktop
# Or use: Settings -> Troubleshoot -> Reset to factory defaults

# Backup important data first!
docker run --rm -v myvolume:/data -v ${PWD}:/backup alpine tar czf /backup/backup.tar.gz -C /data .
```
