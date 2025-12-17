import httpx
import os
import time
from typing import Dict, Any, Optional, Tuple

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get("METEOBLUE_API_KEY")
        self.base_url = "https://my.meteoblue.com/packages"
        # Cache structure: { "lat,lon": { "data": ..., "timestamp": ... } }
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather and forecast from meteoblue API"""
        
        cache_key = f"{latitude},{longitude}"

        # MOCK SUPPORT
        mock_env = os.environ.get("MOCK_WEATHER_API", "false").lower()
        if mock_env == "true":
             # Return random-ish data based on coords to show variation if needed
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
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
        
        try:
            # Meteoblue automatically determines altitude from coordinates
            # No need to pass 'asl' parameter - it will use the correct elevation
            url = f"{self.base_url}/basic-1h_basic-day"
            params = {
                "apikey": self.api_key,
                "lat": latitude,
                "lon": longitude,
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Update cache
                self.cache[cache_key] = {
                    "data": data,
                    "timestamp": time.time()
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
            location = "Unknown Location"
            if "metadata" in weather_data:
                location = weather_data["metadata"].get("name", location)
            lines.append(f"Location: {location}")

            # 2. Daily Max/Min (Today)
            day = weather_data.get("data_day", {})
            max_t = day.get("temperature_max", ["N/A"])[0] if day.get("temperature_max") else "N/A"
            min_t = day.get("temperature_min", ["N/A"])[0] if day.get("temperature_min") else "N/A"
            lines.append(f"Day Max: {max_t}°C | Day Min: {min_t}°C")

            # 3. Current Conditions
            d1h = weather_data.get("data_1h", {})
            curr_temp = d1h.get("temperature", [0])[0] if d1h.get("temperature") else 0
            curr_wind = d1h.get("windspeed", [0])[0] if d1h.get("windspeed") else 0
            curr_code = d1h.get("pictocode", [1])[0] if d1h.get("pictocode") else 1
            
            curr_img = self._get_image_for_condition(curr_code, curr_wind)
            lines.append(f"Current Temp: {curr_temp}°C")
            lines.append(f"Current Condition: {curr_img}")
            
            # 4. Hourly Forecast
            lines.append("\nForecast (Next 5 Hours):")
            temperatures = d1h.get("temperature", [])
            windspeeds = d1h.get("windspeed", [])
            pictocodes = d1h.get("pictocode", [])
            
            for i in range(1, 6):
                if i < len(temperatures):
                    f_temp = temperatures[i]
                    f_wind = windspeeds[i] if i < len(windspeeds) else 0
                    f_code = pictocodes[i] if i < len(pictocodes) else 1
                    f_img = self._get_image_for_condition(f_code, f_wind)
                    lines.append(f"+{i}h: {f_temp}°C [{f_img}]")
                else:
                    lines.append(f"+{i}h: N/A")
            
            return "\n".join(lines)

        except Exception as e:
            return f"Error formatting weather data: {str(e)}"

# Create a singleton instance for use in the server
weather_service = WeatherService()