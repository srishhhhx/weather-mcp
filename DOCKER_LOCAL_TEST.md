# Docker Local Testing Guide 🐳

## Quick Start

### 1. Start Docker Desktop
```bash
# Open Docker Desktop application
# Wait for it to fully start (whale icon in menu bar)
```

### 2. Run Test Script
```bash
./test_docker.sh
```

This will:
- ✅ Check Docker is running
- ✅ Build the Docker image
- ✅ Start the container
- ✅ Test all endpoints
- ✅ Show logs and status

---

## Manual Testing

### Build Image
```bash
docker build -t weather-mcp-api .
```

### Run Container
```bash
docker run -d \
  --name weather-api \
  -p 8000:8000 \
  -e OPENWEATHER_API_KEY=your_key_here \
  -e CACHE_TTL=600 \
  weather-mcp-api
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Weather (Bangalore)
curl http://localhost:8000/weather/12.9716/77.5946

# Forecast (Delhi)
curl http://localhost:8000/forecast/28.7041/77.1025

# API docs
open http://localhost:8000/docs
```

### View Logs
```bash
docker logs -f weather-api
```

### Stop Container
```bash
docker stop weather-api
docker rm weather-api
```

---

## Troubleshooting

### Docker daemon not running
```bash
# Start Docker Desktop application
# Wait for it to fully start
```

### Port already in use
```bash
# Stop existing container
docker stop weather-api
docker rm weather-api

# Or use different port
docker run -d -p 8001:8000 ...
```

### Build fails
```bash
# Check Dockerfile syntax
cat Dockerfile

# Check all files exist
ls -la weather_api_http.py weather_server_free.py requirements-prod.txt
```

### Container exits immediately
```bash
# Check logs
docker logs weather-api

# Common issues:
# - Missing OPENWEATHER_API_KEY
# - Import errors
# - Port conflicts
```

---

## Docker Commands Reference

### Images
```bash
# List images
docker images

# Remove image
docker rmi weather-mcp-api

# Check image size
docker images weather-mcp-api --format "{{.Size}}"
```

### Containers
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop weather-api

# Remove container
docker rm weather-api

# Remove all stopped containers
docker container prune
```

### Logs
```bash
# View logs
docker logs weather-api

# Follow logs
docker logs -f weather-api

# Last 50 lines
docker logs --tail 50 weather-api
```

### Exec into Container
```bash
# Open shell
docker exec -it weather-api /bin/bash

# Run command
docker exec weather-api curl http://localhost:8000/health
```

---

## Expected Output

### Successful Build
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile: 1.23kB
 => [internal] load .dockerignore
 => [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY requirements-prod.txt .
 => [4/6] RUN pip install --no-cache-dir -r requirements-prod.txt
 => [5/6] COPY weather_api_http.py weather_server_free.py .
 => [6/6] RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
 => exporting to image
 => => naming to docker.io/library/weather-mcp-api
```

### Successful Run
```
$ docker ps
CONTAINER ID   IMAGE              STATUS         PORTS
abc123def456   weather-mcp-api    Up 2 minutes   0.0.0.0:8000->8000/tcp
```

### Health Check
```json
{
  "status": "healthy",
  "service": "weather-mcp-api",
  "api_configured": true,
  "cache_ttl": 600
}
```

---

## Performance Metrics

### Image Size
```
Base image:     ~150MB
+ Dependencies: ~50MB
+ App code:     <1MB
= Total:        ~200MB
```

### Build Time
- First build: 2-3 minutes
- Cached build: 30-60 seconds

### Container Resources
- Memory: ~100-150MB
- CPU: <5% idle, ~20% under load
- Startup: ~5 seconds

---

## Next Steps

Once local testing passes:

1. **Commit to Git**
```bash
git add .
git commit -m "Docker deployment ready and tested"
git push origin main
```

2. **Deploy to Render**
- Render will use the same Dockerfile
- Same build process
- Same container configuration

3. **Verify Production**
```bash
curl https://weather-mcp-api.onrender.com/health
```

---

## Tips

### Speed Up Builds
```dockerfile
# Dependencies change less often
# Copy them first for better caching
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

# App code changes more often
# Copy it last
COPY weather_api_http.py weather_server_free.py .
```

### Reduce Image Size
```dockerfile
# Use slim base image
FROM python:3.11-slim

# Clean up after install
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Don't cache pip downloads
RUN pip install --no-cache-dir -r requirements-prod.txt
```

### Better Security
```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Don't write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
```

---

## Summary

✅ Docker installed
✅ Test script ready
✅ Manual commands documented
✅ Troubleshooting guide included

**Run `./test_docker.sh` to test your Docker setup!** 🚀
