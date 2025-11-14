"""
FastMCP Weather Server - FREE TIER VERSION
Uses OpenWeather FREE APIs (no subscription required):
- Current Weather Data API 2.5
- 5 Day / 3 Hour Forecast API
"""
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("weather-server")

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CACHE_TTL = int(os.getenv("CACHE_TTL", "600"))  # 10 minutes default
PORT = int(os.getenv("PORT", "10000"))

# In-memory cache
cache: Dict[str, Dict[str, Any]] = {}

print(f"Starting Weather MCP Server (FREE TIER) on port {PORT}")
print(f"Cache TTL: {CACHE_TTL} seconds")
print(f"API Key configured: {bool(OPENWEATHER_API_KEY)}")


def get_cache_key(lat: float, lon: float, endpoint: str) -> str:
    """Generate cache key"""
    return f"{lat}|{lon}|{endpoint}"


def get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve data from cache if not expired"""
    if key in cache:
        entry = cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            print(f"[CACHE HIT] {key}")
            return entry["data"]
        else:
            print(f"[CACHE EXPIRED] {key}")
            # Don't delete - keep for fallback
    print(f"[CACHE MISS] {key}")
    return None


def set_cache(key: str, data: Dict[str, Any]) -> None:
    """Store data in cache with timestamp"""
    cache[key] = {
        "data": data,
        "timestamp": time.time()
    }
    print(f"[CACHE SET] {key}")


async def fetch_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather from FREE Current Weather API 2.5"""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not set in environment")
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
        elapsed = time.time() - start_time
        print(f"[API SUCCESS] Current Weather API responded in {elapsed:.2f}s")
        
        return response.json()
    
    except httpx.HTTPStatusError as e:
        print(f"[API ERROR] HTTP {e.response.status_code}: {e.response.text}")
        raise Exception(f"OpenWeather API error: {e.response.status_code}")
    
    except httpx.RequestError as e:
        print(f"[API ERROR] Request failed: {str(e)}")
        raise Exception(f"Failed to connect to OpenWeather API: {str(e)}")


async def fetch_forecast_data(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch 5-day forecast from FREE 5 Day / 3 Hour Forecast API"""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not set in environment")
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
        elapsed = time.time() - start_time
        print(f"[API SUCCESS] Forecast API responded in {elapsed:.2f}s")
        
        return response.json()
    
    except httpx.HTTPStatusError as e:
        print(f"[API ERROR] HTTP {e.response.status_code}: {e.response.text}")
        raise Exception(f"OpenWeather API error: {e.response.status_code}")
    
    except httpx.RequestError as e:
        print(f"[API ERROR] Request failed: {str(e)}")
        raise Exception(f"Failed to connect to OpenWeather API: {str(e)}")


def normalize_current_weather(data: Dict[str, Any], cached: bool = False) -> Dict[str, Any]:
    """Normalize Current Weather API 2.5 response"""
    # If data is already normalized, return copy with updated cached flag
    if "provider" in data and data.get("provider") == "openweather":
        result = data.copy()
        result["cached"] = cached
        return result
    
    # Extract rainfall from rain object if present
    rainfall = 0.0
    if "rain" in data and "1h" in data["rain"]:
        rainfall = data["rain"]["1h"]
    elif "rain" in data and "3h" in data["rain"]:
        rainfall = data["rain"]["3h"] / 3  # Convert 3h to 1h average
    
    return {
        "temperature": data.get("main", {}).get("temp", 0),
        "humidity": data.get("main", {}).get("humidity", 0),
        "rainfall": rainfall,
        "wind_speed": data.get("wind", {}).get("speed", 0),
        "description": data.get("weather", [{}])[0].get("description", "unknown"),
        "provider": "openweather",
        "cached": cached,
        "timestamp": datetime.fromtimestamp(data.get("dt", time.time())).isoformat()
    }


def normalize_forecast(data: Dict[str, Any], days: int, cached: bool = False) -> Dict[str, Any]:
    """
    Normalize 5 Day / 3 Hour Forecast API response
    Groups 3-hour forecasts into daily summaries
    """
    forecast_list = []
    
    # Group forecasts by day
    daily_data = {}
    for item in data.get("list", [])[:days * 8]:  # 8 forecasts per day (3-hour intervals)
        date = datetime.fromtimestamp(item["dt"]).date().isoformat()
        
        if date not in daily_data:
            daily_data[date] = {
                "temps": [],
                "humidity": [],
                "rainfall": [],
                "descriptions": []
            }
        
        daily_data[date]["temps"].append(item["main"]["temp"])
        daily_data[date]["humidity"].append(item["main"]["humidity"])
        
        # Extract rainfall
        rain = 0.0
        if "rain" in item and "3h" in item["rain"]:
            rain = item["rain"]["3h"]
        daily_data[date]["rainfall"].append(rain)
        
        if item.get("weather"):
            daily_data[date]["descriptions"].append(item["weather"][0]["description"])
    
    # Create daily summaries
    for date, day_data in list(daily_data.items())[:days]:
        forecast_list.append({
            "date": date,
            "temp_min": min(day_data["temps"]),
            "temp_max": max(day_data["temps"]),
            "humidity": int(sum(day_data["humidity"]) / len(day_data["humidity"])),
            "rainfall": sum(day_data["rainfall"]),
            "description": day_data["descriptions"][0] if day_data["descriptions"] else "unknown"
        })
    
    return {
        "forecast": forecast_list,
        "provider": "openweather",
        "cached": cached,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Get current weather for given coordinates (FREE TIER)
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Normalized weather data with temperature, humidity, rainfall, wind_speed, description
    """
    cache_key = get_cache_key(lat, lon, "current")
    
    # Try cache first
    cached_data = get_from_cache(cache_key)
    if cached_data:
        result = cached_data.copy()
        result["cached"] = True
        return result
    
    # Fetch from API
    try:
        raw_data = await fetch_current_weather(lat, lon)
        normalized = normalize_current_weather(raw_data, cached=False)
        set_cache(cache_key, normalized)
        return normalized
    
    except Exception as e:
        # Try to return stale cache as fallback
        if cache_key in cache:
            print(f"[FALLBACK] Returning stale cache due to error: {str(e)}")
            stale_data = cache[cache_key]["data"]
            stale_data["cached"] = True
            stale_data["stale"] = True
            return stale_data
        raise


@mcp.tool()
async def get_forecast(lat: float, lon: float, days: int = 5) -> Dict[str, Any]:
    """
    Get weather forecast for given coordinates (FREE TIER - max 5 days)
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        days: Number of days (1-5, default 5)
    
    Returns:
        5-day forecast with daily min/max temps, humidity, rainfall, description
    """
    if days < 1 or days > 5:
        raise ValueError("days must be between 1 and 5 for free tier")
    
    cache_key = get_cache_key(lat, lon, f"forecast_{days}")
    
    # Try cache first
    cached_data = get_from_cache(cache_key)
    if cached_data:
        result = cached_data.copy()
        result["cached"] = True
        return result
    
    # Fetch from API
    try:
        raw_data = await fetch_forecast_data(lat, lon)
        normalized = normalize_forecast(raw_data, days, cached=False)
        set_cache(cache_key, normalized)
        return normalized
    
    except Exception as e:
        # Try to return stale cache as fallback
        if cache_key in cache:
            print(f"[FALLBACK] Returning stale cache due to error: {str(e)}")
            stale_data = cache[cache_key]["data"]
            stale_data["cached"] = True
            stale_data["stale"] = True
            return stale_data
        raise


@mcp.tool()
async def health_check() -> Dict[str, str]:
    """
    Check server health
    
    Returns:
        Server status and timestamp
    """
    return {
        "status": "healthy",
        "service": "weather-mcp-server-free-tier",
        "timestamp": datetime.now().isoformat(),
        "api": "OpenWeather Free Tier (2.5)"
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
