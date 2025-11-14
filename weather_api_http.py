"""
HTTP API Wrapper for Weather MCP Server (Free Tier)
Exposes weather endpoints via HTTP for easy integration

Run: python weather_api_http.py
Access: http://localhost:8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import from free tier server
from weather_server_free import (
    get_weather as mcp_get_weather,
    get_forecast as mcp_get_forecast,
    OPENWEATHER_API_KEY,
    CACHE_TTL
)

# Initialize FastAPI
app = FastAPI(
    title="Weather MCP API",
    description="HTTP API for Weather MCP Server (Free Tier)",
    version="1.0.0"
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeatherRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")


class ForecastRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    days: int = Field(5, ge=1, le=5, description="Number of days (1-5)")


@app.get("/")
async def root():
    """API information and endpoints"""
    return {
        "service": "Weather MCP API (Free Tier)",
        "version": "1.0.0",
        "status": "operational",
        "api_key_configured": bool(OPENWEATHER_API_KEY),
        "cache_ttl": f"{CACHE_TTL} seconds",
        "endpoints": {
            "GET /": "This information page",
            "GET /health": "Health check",
            "POST /weather": "Get current weather (lat, lon)",
            "POST /forecast": "Get forecast (lat, lon, days)",
            "GET /weather/{lat}/{lon}": "Get current weather (URL params)",
            "GET /forecast/{lat}/{lon}": "Get 5-day forecast (URL params)",
            "GET /forecast/{lat}/{lon}/{days}": "Get N-day forecast (URL params)"
        },
        "examples": {
            "current_weather": "GET http://localhost:8000/weather/12.9716/77.5946",
            "forecast": "GET http://localhost:8000/forecast/28.7041/77.1025",
            "forecast_3_days": "GET http://localhost:8000/forecast/40.7128/-74.0060/3"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "weather-mcp-api",
        "api_configured": bool(OPENWEATHER_API_KEY),
        "cache_ttl": CACHE_TTL
    }


@app.post("/weather")
async def get_weather_post(request: WeatherRequest):
    """
    Get current weather for coordinates (POST)
    
    Body:
    {
        "lat": 12.9716,
        "lon": 77.5946
    }
    """
    try:
        result = await mcp_get_weather(request.lat, request.lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/{lat}/{lon}")
async def get_weather_get(lat: float, lon: float):
    """
    Get current weather for coordinates (GET)
    
    Example: GET /weather/12.9716/77.5946
    """
    try:
        result = await mcp_get_weather(lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast")
async def get_forecast_post(request: ForecastRequest):
    """
    Get weather forecast (POST)
    
    Body:
    {
        "lat": 28.7041,
        "lon": 77.1025,
        "days": 5
    }
    """
    try:
        result = await mcp_get_forecast(request.lat, request.lon, request.days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast/{lat}/{lon}")
async def get_forecast_get(lat: float, lon: float):
    """
    Get 5-day weather forecast (GET)
    
    Example: GET /forecast/28.7041/77.1025
    """
    try:
        result = await mcp_get_forecast(lat, lon, days=5)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast/{lat}/{lon}/{days}")
async def get_forecast_get_days(lat: float, lon: float, days: int):
    """
    Get N-day weather forecast (GET)
    
    Example: GET /forecast/40.7128/-74.0060/3
    """
    if days < 1 or days > 5:
        raise HTTPException(status_code=400, detail="days must be between 1 and 5")
    
    try:
        result = await mcp_get_forecast(lat, lon, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌤️  Weather MCP HTTP API Server (Free Tier)")
    print("="*70)
    print(f"\n📍 Server starting on: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔍 Interactive API: http://localhost:8000/redoc")
    print(f"\n🌐 Example URLs:")
    print(f"   Current Weather: http://localhost:8000/weather/12.9716/77.5946")
    print(f"   5-Day Forecast:  http://localhost:8000/forecast/28.7041/77.1025")
    print(f"   3-Day Forecast:  http://localhost:8000/forecast/40.7128/-74.0060/3")
    print(f"\n⚡ Cache TTL: {CACHE_TTL} seconds")
    print(f"🔑 API Key: {'Configured ✅' if OPENWEATHER_API_KEY else 'Not configured ❌'}")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
