# Docker Commands Cheatsheet

## Container Management

### Run Containers

```bash
# Run container
docker run nginx

# Run in detached mode
docker run -d nginx

# Run with name
docker run -d --name web nginx

# Run with port mapping
docker run -d -p 8080:80 nginx

# Run with environment variables
docker run -d -e "KEY=value" myapp

# Run with volume
docker run -d -v mydata:/app/data myapp

# Run with network
docker run -d --network mynetwork myapp

# Run with resource limits
docker run -d --memory="512m" --cpus="1.0" myapp

# Run with restart policy
docker run -d --restart unless-stopped nginx

# Run interactive shell
docker run -it ubuntu bash

# Run and remove after exit
docker run --rm myapp
```

### List Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List container IDs only
docker ps -q

# List with formatting
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Filter containers
docker ps --filter "name=web"
docker ps --filter "status=running"
```

### Container Lifecycle

```bash
# Start container
docker start container_name

# Stop container
docker stop container_name

# Restart container
docker restart container_name

# Pause container
docker pause container_name

# Unpause container
docker unpause container_name

# Kill container
docker kill container_name

# Remove container
docker rm container_name

# Remove running container
docker rm -f container_name

# Remove all stopped containers
docker container prune
```

### Container Information

```bash
# View container logs
docker logs container_name

# Follow logs
docker logs -f container_name

# Last 100 lines
docker logs --tail 100 container_name

# Logs with timestamps
docker logs -t container_name

# Inspect container
docker inspect container_name

# View container stats
docker stats container_name

# View container processes
docker top container_name

# View container port mappings
docker port container_name
```

### Execute Commands

```bash
# Execute command in running container
docker exec container_name command

# Interactive shell
docker exec -it container_name bash
docker exec -it container_name sh

# Execute as specific user
docker exec -u user container_name command

# Execute with environment variables
docker exec -e KEY=value container_name command
```

### Copy Files

```bash
# Copy from container to host
docker cp container_name:/path/in/container /host/path

# Copy from host to container
docker cp /host/path container_name:/path/in/container
```

## Image Management

### Build Images

```bash
# Build image
docker build -t myapp:latest .

# Build with specific Dockerfile
docker build -t myapp -f Dockerfile.prod .

# Build with build arguments
docker build --build-arg VERSION=1.0 -t myapp .

# Build without cache
docker build --no-cache -t myapp .

# Build specific target in multi-stage
docker build --target production -t myapp .

# Build with progress output
docker build --progress=plain -t myapp .
```

### List Images

```bash
# List images
docker images

# List all images including intermediate
docker images -a

# List image IDs only
docker images -q

# Filter images
docker images --filter "dangling=true"
docker images --filter "reference=myapp:*"
```

### Image Operations

```bash
# Pull image
docker pull nginx:latest

# Push image
docker push myrepo/myapp:latest

# Tag image
docker tag myapp:latest myrepo/myapp:v1.0

# Remove image
docker rmi image_name

# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a

# Save image to tar
docker save myapp:latest -o myapp.tar

# Load image from tar
docker load -i myapp.tar

# Export container to tar
docker export container_name -o container.tar

# Import container from tar
docker import container.tar myapp:latest
```

### Image Information

```bash
# Inspect image
docker inspect image_name

# View image history
docker history image_name

# View image layers
docker image inspect --format='{{json .RootFS.Layers}}' image_name
```

## Volume Management

```bash
# Create volume
docker volume create myvolume

# List volumes
docker volume ls

# Inspect volume
docker volume inspect myvolume

# Remove volume
docker volume rm myvolume

# Remove all unused volumes
docker volume prune

# Backup volume
docker run --rm -v myvolume:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# Restore volume
docker run --rm -v myvolume:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
```

## Network Management

```bash
# Create network
docker network create mynetwork

# List networks
docker network ls

# Inspect network
docker network inspect mynetwork

# Connect container to network
docker network connect mynetwork container_name

# Disconnect container from network
docker network disconnect mynetwork container_name

# Remove network
docker network rm mynetwork

# Remove all unused networks
docker network prune
```

## Docker Compose

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# List services
docker-compose ps

# Execute command in service
docker-compose exec service_name command

# Scale services
docker-compose up -d --scale web=3

# Restart services
docker-compose restart

# Pause services
docker-compose pause

# Unpause services
docker-compose unpause

# View service configuration
docker-compose config

# Pull images
docker-compose pull

# Build images
docker-compose build

# Push images
docker-compose push
```

## System Management

```bash
# View system information
docker info

# View Docker version
docker version

# View disk usage
docker system df

# Clean up system
docker system prune

# Clean up everything
docker system prune -a --volumes

# View events
docker events

# View system-wide info
docker system info
```

## Registry Operations

```bash
# Login to registry
docker login

# Login to specific registry
docker login registry.example.com

# Logout
docker logout

# Search images
docker search nginx

# Pull from private registry
docker pull registry.example.com/myapp:latest

# Push to private registry
docker push registry.example.com/myapp:latest

# Tag for private registry
docker tag myapp:latest registry.example.com/myapp:latest
```

## Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Join swarm as worker
docker swarm join --token TOKEN HOST:PORT

# Join swarm as manager
docker swarm join --token TOKEN HOST:PORT

# Leave swarm
docker swarm leave

# List nodes
docker node ls

# Inspect node
docker node inspect node_id

# Create service
docker service create --name web --replicas 3 -p 80:80 nginx

# List services
docker service ls

# Scale service
docker service scale web=5

# Update service
docker service update --image nginx:alpine web

# Remove service
docker service rm web

# View service logs
docker service logs web

# Inspect service
docker service inspect web
```

## Security Scanning

```bash
# Scan image with Docker Scout (if available)
docker scout cves myapp:latest

# Scan with Trivy
trivy image myapp:latest

# Scan with Snyk
snyk container test myapp:latest

# Scan with Clair
clairctl analyze myapp:latest
```

## Troubleshooting

```bash
# View container logs with details
docker logs --details container_name

# Stream container stats
docker stats --no-stream

# Inspect container network
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name

# Check container health
docker inspect --format='{{.State.Health.Status}}' container_name

# View container environment variables
docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' container_name

# Debug container startup issues
docker events --filter container=container_name

# Attach to container
docker attach container_name

# View container changes
docker diff container_name

# Export container filesystem
docker export container_name -o container.tar
```

## Advanced Operations

```bash
# Run with custom DNS
docker run -d --dns 8.8.8.8 nginx

# Run with host networking
docker run -d --network host nginx

# Run with privileged mode
docker run -d --privileged myapp

# Add capability
docker run -d --cap-add NET_ADMIN myapp

# Drop capability
docker run -d --cap-drop ALL myapp

# Set memory limit
docker run -d --memory="512m" --memory-swap="1g" myapp

# Set CPU limit
docker run -d --cpus="1.5" --cpu-shares=1024 myapp

# Set device
docker run -d --device=/dev/sda:/dev/xvda myapp

# Run with read-only filesystem
docker run -d --read-only --tmpfs /tmp myapp

# Run with user
docker run -d --user 1000:1000 myapp

# Run with working directory
docker run -d --workdir /app myapp

# Run with hostname
docker run -d --hostname myhost myapp

# Run with extra hosts
docker run -d --add-host=api.example.com:192.168.1.100 myapp
```

## Best Practices Commands

```bash
# Build multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .

# Create and use builder
docker buildx create --name mybuilder --use

# Build with cache from registry
docker build --cache-from myrepo/myapp:latest -t myapp:latest .

# Health check
docker run -d --health-cmd="curl -f http://localhost/ || exit 1" \
           --health-interval=30s \
           --health-timeout=3s \
           --health-retries=3 \
           nginx

# Label management
docker run -d --label "environment=production" --label "app=web" nginx

# Filter by label
docker ps --filter "label=environment=production"

# Remove containers by label
docker rm $(docker ps -a --filter "label=environment=dev" -q)
```
