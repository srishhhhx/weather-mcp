#!/bin/bash
# Test Docker Build and Run Locally

set -e

echo "🐳 Docker Local Test Script"
echo "============================"
echo ""

# Check if Docker is running
echo "1️⃣ Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  - Open Docker Desktop application"
    echo "  - Wait for it to start"
    echo "  - Then run this script again"
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check if .env exists
echo "2️⃣ Checking environment..."
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please create .env with OPENWEATHER_API_KEY"
    exit 1
fi

# Load environment
source .env
if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "❌ OPENWEATHER_API_KEY not set in .env"
    exit 1
fi
echo "✅ API key configured"
echo ""

# Build Docker image
echo "3️⃣ Building Docker image..."
echo "This may take 2-3 minutes on first build..."
docker build -t weather-mcp-api . || {
    echo "❌ Docker build failed"
    exit 1
}
echo "✅ Docker image built successfully"
echo ""

# Check image size
IMAGE_SIZE=$(docker images weather-mcp-api --format "{{.Size}}")
echo "📦 Image size: $IMAGE_SIZE"
echo ""

# Stop and remove existing container if running
echo "4️⃣ Cleaning up old containers..."
docker stop weather-api-test 2>/dev/null || true
docker rm weather-api-test 2>/dev/null || true
echo "✅ Cleanup complete"
echo ""

# Run container
echo "5️⃣ Starting container..."
docker run -d \
  --name weather-api-test \
  -p 8000:8000 \
  -e OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY" \
  -e CACHE_TTL=600 \
  weather-mcp-api

echo "✅ Container started"
echo ""

# Wait for container to be ready
echo "6️⃣ Waiting for server to start..."
sleep 5

# Check if container is running
if ! docker ps | grep -q weather-api-test; then
    echo "❌ Container failed to start"
    echo ""
    echo "Container logs:"
    docker logs weather-api-test
    exit 1
fi
echo "✅ Container is running"
echo ""

# Test health endpoint
echo "7️⃣ Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
    echo "Response: $HEALTH_RESPONSE"
else
    echo "❌ Health check failed"
    docker logs weather-api-test
    exit 1
fi
echo ""

# Test weather endpoint
echo "8️⃣ Testing weather endpoint (Bangalore)..."
WEATHER_RESPONSE=$(curl -s http://localhost:8000/weather/12.9716/77.5946)
if [ $? -eq 0 ]; then
    echo "✅ Weather endpoint works"
    echo "Response (first 200 chars):"
    echo "$WEATHER_RESPONSE" | head -c 200
    echo "..."
else
    echo "❌ Weather endpoint failed"
    docker logs weather-api-test
    exit 1
fi
echo ""
echo ""

# Show container info
echo "9️⃣ Container information:"
echo "========================"
docker ps --filter name=weather-api-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Show logs
echo "🔟 Recent logs:"
echo "==============="
docker logs --tail 20 weather-api-test
echo ""

# Summary
echo "============================"
echo "✅ All tests passed!"
echo "============================"
echo ""
echo "Your Docker container is running at:"
echo "  http://localhost:8000"
echo ""
echo "Available endpoints:"
echo "  http://localhost:8000/health"
echo "  http://localhost:8000/docs"
echo "  http://localhost:8000/weather/12.9716/77.5946"
echo ""
echo "To stop the container:"
echo "  docker stop weather-api-test"
echo ""
echo "To view logs:"
echo "  docker logs -f weather-api-test"
echo ""
echo "To remove container:"
echo "  docker rm -f weather-api-test"
echo ""
echo "Ready to deploy to Render! 🚀"
