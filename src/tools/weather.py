import httpx
import os
import time
from typing import Dict, Any, Optional

class WeatherService:
    def __init__(self):
        # Adapted to use os.environ for consistency with the project structure
        self.api_key = os.environ.get("METEOBLUE_API_KEY")
        self.base_url = "https://my.meteoblue.com/packages"
        self.cache: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[float] = None
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather and forecast from meteoblue API"""
        
        # MOCK SUPPORT for testing without API Key
        mock_env = os.environ.get("MOCK_WEATHER_API", "false").lower()
        if mock_env == "true":
             return {
                "metadata": {"name": "Mock City"},
                "data_1h": {
                    "time": ["2023-10-27 12:00"],
                    "temperature": [22.5],
                    "windspeed": [15.0],
                    "precipitation_probability": [0]
                }
            }

        if not self.api_key:
             raise ValueError("Meteoblue API Key is required. Set METEOBLUE_API_KEY env var.")

        # Check cache
        if self.cache and self.cache_timestamp:
            if time.time() - self.cache_timestamp < self.cache_ttl:
                return self.cache
        
        try:
            # meteoblue API endpoint for basic weather
            # Using basic-1h_basic-day package commonly available
            url = f"{self.base_url}/basic-1h_basic-day"
            params = {
                "apikey": self.api_key,
                "lat": latitude,
                "lon": longitude,
                "asl": 0,
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Cache the result
                self.cache = data
                self.cache_timestamp = time.time()
                
                return data
        except Exception as e:
            # Return cached data if available, even if expired
            if self.cache:
                return self.cache
            raise RuntimeError(f"Error fetching weather data: {str(e)}")
    
    def format_weather_for_context(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data as a readable string for context"""
        try:
            # Meteoblue JSON structure handling
            # Usually: data_1h -> { "temperature": [22.5, ...], ... }
            if "data_1h" in weather_data:
                d1h = weather_data["data_1h"]
                
                # Helper to safely get first element
                def get_first(key, unit=""):
                    val = d1h.get(key, [])
                    return f"{val[0]}{unit}" if val else "N/A"

                temp = get_first("temperature", "°C")
                wind = get_first("windspeed", " km/h")
                precip = get_first("precipitation_probability", "%")
                
                return (f"Current Weather:\n"
                        f"- Temperature: {temp}\n"
                        f"- Wind Speed: {wind}\n"
                        f"- Rain Chance: {precip}")
            
            return "Weather information not available or format unrecognized."
        except Exception as e:
            return f"Error formatting weather data: {str(e)}"

# Singleton instance
weather_service = WeatherService()
