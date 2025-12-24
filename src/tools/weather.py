import httpx
import os
import time
from typing import Dict, Any, Optional

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get("METEOBLUE_API_KEY")
        self.base_url = "https://my.meteoblue.com/packages"
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600
        self._client: Optional[httpx.AsyncClient] = None
        self._mock_enabled = os.environ.get("MOCK_WEATHER_API", "false").lower() == "true"
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create persistent HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def close(self):
        """Close HTTP client (call on shutdown)"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather and forecast from meteoblue API"""
        cache_key = f"{latitude},{longitude}"

        if self._mock_enabled:
            return {
                "metadata": {"name": "Mock City"},
                "data_1h": {
                    "time": ["2023-10-27 12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
                    "temperature": [22.5, 23.0, 22.0, 21.0, 20.0, 19.0],
                    "windspeed": [15.0, 10.0, 45.0, 12.0, 10.0, 10.0],
                    "pictocode": [1, 2, 4, 12, 1, 1] 
                },
                "data_day": {
                    "time": ["2023-10-27"],
                    "temperature_max": [25.0],
                    "temperature_min": [18.0]
                }
            }

        if not self.api_key:
            raise ValueError("Meteoblue API Key is required. Set METEOBLUE_API_KEY env var.")

        # Check cache
        now = time.time()
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
        
        try:
            client = await self._get_client()
            url = f"{self.base_url}/basic-1h_basic-day"
            params = {
                "apikey": self.api_key,
                "lat": latitude,
                "lon": longitude,
                "format": "json"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Update cache
            self.cache[cache_key] = {
                "data": data,
                "timestamp": now
            }
            
            return data
        except Exception as e:
            # Return cached data if available (expired) as fallback
            if cache_key in self.cache:
                return self.cache[cache_key]["data"]
            raise RuntimeError(f"Error fetching weather data: {str(e)}")
    
    def _get_image_for_condition(self, pictocode: int, windspeed: float) -> str:
        """Map meteoblue condition to specific image filenames"""
        if windspeed > 30: 
            return "https://cdn.openai.com/API/storybook/windy.png"
        
        if pictocode <= 3:
            return "https://cdn.openai.com/API/storybook/mostly-sunny.png"
        elif pictocode <= 8:
            return "https://cdn.openai.com/API/storybook/mixed-sun.png"
        else:
            return "https://cdn.openai.com/API/storybook/rain.png"

    def format_weather_for_context(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data with images and forecast"""
        try:
            lines = []
            
            # 1. Location
            metadata = weather_data.get("metadata", {})
            location = metadata.get("name", "Unknown Location")
            lines.append(f"Location: {location}")

            # 2. Daily Max/Min (Today)
            day = weather_data.get("data_day", {})
            temp_max = day.get("temperature_max")
            temp_min = day.get("temperature_min")
            max_t = temp_max[0] if temp_max else "N/A"
            min_t = temp_min[0] if temp_min else "N/A"
            lines.append(f"Day Max: {max_t}°C | Day Min: {min_t}°C")

            # 3. Current Conditions
            d1h = weather_data.get("data_1h", {})
            temps = d1h.get("temperature", [])
            winds = d1h.get("windspeed", [])
            codes = d1h.get("pictocode", [])
            
            curr_temp = temps[0] if temps else 0
            curr_wind = winds[0] if winds else 0
            curr_code = codes[0] if codes else 1
            curr_img = self._get_image_for_condition(curr_code, curr_wind)
            lines.append(f"Current Temp: {curr_temp}°C")
            lines.append(f"Current Condition: {curr_img}")
            
            # 4. Hourly Forecast - every 2 hours
            lines.append("\nForecast (Every 2 Hours):")
            for i in range(2, 12, 2):
                if i < len(temps):
                    f_temp = temps[i]
                    f_wind = winds[i] if i < len(winds) else 0
                    f_code = codes[i] if i < len(codes) else 1
                    f_img = self._get_image_for_condition(f_code, f_wind)
                    lines.append(f"+{i}h: {f_temp}°C [{f_img}]")
                else:
                    lines.append(f"+{i}h: N/A")
            
            return "\n".join(lines)

        except Exception as e:
            return f"Error formatting weather data: {str(e)}"

# Create a singleton instance for use in the server
weather_service = WeatherService()