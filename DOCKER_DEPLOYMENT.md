# Docker Deployment Guide 🐳

## Why Docker is Better

### ✅ Advantages of Docker Deployment

1. **Consistency** - Same environment everywhere (dev, staging, prod)
2. **Isolation** - No dependency conflicts
3. **Portability** - Deploy anywhere (Render, AWS, GCP, Azure)
4. **Reproducibility** - Exact same build every time
5. **Security** - Runs as non-root user
6. **Health Checks** - Built-in health monitoring
7. **Easy Rollback** - Just redeploy previous image

### ⚠️ Without Docker
- Python version mismatches
- Dependency conflicts
- Different environments
- Harder to debug

---

## 🐳 Docker Setup

### Files Included

```
✅ Dockerfile           # Container definition
✅ .dockerignore        # Files to exclude from build
✅ render.yaml          # Render config (uses Docker)
```

### Dockerfile Features

- ✅ Python 3.11 slim base
- ✅ Production dependencies only
- ✅ Non-root user (security)
- ✅ Health check endpoint
- ✅ Optimized layers
- ✅ Small image size (~200MB)

---

## 🚀 Deployment Options

### Option 1: Render with Docker (Recommended) ⭐

**Advantages:**
- Free tier available
- Automatic HTTPS
- Auto-deploy on git push
- Built-in health checks
- Easy environment variables

**Steps:**

1. **Push to GitHub**
```bash
git add .
git commit -m "Docker deployment ready"
git push origin main
```

2. **Deploy on Render**
- Go to https://render.com
- New → Web Service
- Connect GitHub repo
- Render auto-detects Dockerfile
- Add `OPENWEATHER_API_KEY` env var
- Deploy!

**Your API will be live at:**
```
https://weather-mcp-api.onrender.com
```

---

### Option 2: Local Docker Testing

**Test before deploying:**

```bash
# Build image
docker build -t weather-mcp-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENWEATHER_API_KEY=your_key_here \
  -e CACHE_TTL=600 \
  --name weather-api \
  weather-mcp-api

# Test
curl http://localhost:8000/health
curl http://localhost:8000/weather/12.9716/77.5946

# View logs
docker logs weather-api

# Stop container
docker stop weather-api
docker rm weather-api
```

---

### Option 3: Docker Compose (Local Development)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  weather-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - CACHE_TTL=600
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

**Run:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

### Option 4: Deploy to Other Platforms

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
docker build -t weather-mcp-api .
docker tag weather-mcp-api:latest YOUR_ECR_URL/weather-mcp-api:latest
docker push YOUR_ECR_URL/weather-mcp-api:latest
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT/weather-mcp-api
gcloud run deploy weather-mcp-api \
  --image gcr.io/YOUR_PROJECT/weather-mcp-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Build and push to ACR
az acr build --registry YOUR_REGISTRY --image weather-mcp-api .
az container create \
  --resource-group YOUR_RG \
  --name weather-mcp-api \
  --image YOUR_REGISTRY.azurecr.io/weather-mcp-api \
  --dns-name-label weather-mcp \
  --ports 8000
```

---

## 📊 Docker vs Non-Docker Comparison

| Feature | Docker ✅ | Non-Docker ❌ |
|---------|----------|---------------|
| **Consistency** | Same everywhere | May differ |
| **Dependencies** | Isolated | Can conflict |
| **Python Version** | Fixed (3.11) | May vary |
| **Security** | Non-root user | Root by default |
| **Health Checks** | Built-in | Manual |
| **Portability** | Deploy anywhere | Platform-specific |
| **Rollback** | Easy (previous image) | Complex |
| **Image Size** | ~200MB | N/A |
| **Build Time** | ~2-3 min | ~1-2 min |
| **Cold Start** | Slightly slower | Faster |

---

## 🔧 Dockerfile Explained

```dockerfile
FROM python:3.11-slim
# ↑ Small base image (~150MB)

WORKDIR /app
# ↑ Set working directory

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000
# ↑ Optimize Python for containers

RUN apt-get update && apt-get install -y --no-install-recommends curl
# ↑ Install curl for health checks

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
# ↑ Install dependencies (cached layer)

COPY weather_api_http.py weather_server_free.py .
# ↑ Copy application code

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
# ↑ Run as non-root for security

EXPOSE 8000
# ↑ Document port

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
# ↑ Auto health monitoring

CMD ["uvicorn", "weather_api_http:app", "--host", "0.0.0.0", "--port", "8000"]
# ↑ Start server
```

---

## 🎯 Render Deployment (Step-by-Step)

### 1. Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Docker deployment ready"
git push origin main
```

### 2. Create Render Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Render auto-detects `Dockerfile` ✅
5. Configure:
   - **Name:** weather-mcp-api
   - **Region:** Oregon (US West)
   - **Branch:** main
   - **Runtime:** Docker (auto-detected)
   - **Plan:** Free

### 3. Add Environment Variables

Click "Advanced" → Add:
```
OPENWEATHER_API_KEY = your_api_key_here
CACHE_TTL = 600
```

### 4. Deploy

- Click "Create Web Service"
- Wait 3-5 minutes for build
- Status changes to "Live" ✅

### 5. Verify

```bash
# Health check
curl https://weather-mcp-api.onrender.com/health

# Get weather
curl https://weather-mcp-api.onrender.com/weather/12.9716/77.5946
```

---

## 🔍 Troubleshooting

### Build Fails

**Check:**
1. Dockerfile syntax
2. requirements-prod.txt exists
3. All files committed to git

**Fix:**
```bash
# Test locally
docker build -t test-build .
```

### Container Won't Start

**Check logs in Render dashboard**

Common issues:
- Missing environment variables
- Port mismatch
- Import errors

**Fix:**
```bash
# Test locally
docker run -e OPENWEATHER_API_KEY=test weather-mcp-api
docker logs CONTAINER_ID
```

### Health Check Failing

**Check:**
- `/health` endpoint returns 200
- Container is listening on correct port

**Fix:**
```bash
# Test health endpoint
docker exec CONTAINER_ID curl http://localhost:8000/health
```

---

## 📈 Performance

### Image Size
```
Base image (python:3.11-slim):  ~150MB
+ Dependencies:                 ~50MB
+ Application code:             <1MB
= Total:                        ~200MB
```

### Build Time
- **First build:** 3-5 minutes
- **Cached builds:** 30-60 seconds
- **Render deployment:** 3-5 minutes

### Runtime Performance
- **Cold start:** ~5-10 seconds
- **Response time:** Same as non-Docker
- **Memory usage:** ~100-150MB

---

## ✅ Benefits Summary

### For Development
- ✅ Consistent environment
- ✅ Easy to test locally
- ✅ No "works on my machine"

### For Deployment
- ✅ Deploy anywhere
- ✅ Easy rollback
- ✅ Built-in health checks
- ✅ Better security

### For Maintenance
- ✅ Clear dependencies
- ✅ Version control
- ✅ Easy updates

---

## 🎉 Conclusion

**Docker deployment is BETTER because:**

1. ✅ **More reliable** - Same environment everywhere
2. ✅ **More secure** - Non-root user, isolated
3. ✅ **More portable** - Deploy anywhere
4. ✅ **Easier to maintain** - Clear dependencies
5. ✅ **Production-ready** - Health checks, monitoring

**Your Weather MCP API is now Docker-ready!** 🐳

---

## 📝 Quick Commands

```bash
# Build
docker build -t weather-mcp-api .

# Run locally
docker run -d -p 8000:8000 \
  -e OPENWEATHER_API_KEY=your_key \
  weather-mcp-api

# Test
curl http://localhost:8000/health

# Deploy to Render
git push origin main  # Auto-deploys!

# View logs
docker logs CONTAINER_ID
```

**Ready to deploy with Docker!** 🚀
