import httpx
import os
import time
from typing import Dict, Any, Optional

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get("METEOBLUE_API_KEY")
        self.base_url = "https://my.meteoblue.com/packages"
        self.cache: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[float] = None
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather and forecast from meteoblue API"""
        
        # MOCK SUPPORT
        mock_env = os.environ.get("MOCK_WEATHER_API", "false").lower()
        if mock_env == "true":
             return {
                "metadata": {"name": "Mock City"},
                "data_1h": {
                    "time": ["2023-10-27 12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
                    "temperature": [22.5, 23.0, 22.0, 21.0, 20.0, 19.0],
                    "windspeed": [15.0, 10.0, 45.0, 12.0, 10.0, 10.0],
                    "pictocode": [1, 2, 4, 12, 1, 1] # Sunny, Sunny, Cloudy, Rain, Sunny, Sunny
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
        if self.cache and self.cache_timestamp:
            if time.time() - self.cache_timestamp < self.cache_ttl:
                return self.cache
        
        try:
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
                
                self.cache = data
                self.cache_timestamp = time.time()
                
                return data
        except Exception as e:
            if self.cache: return self.cache
            raise RuntimeError(f"Error fetching weather data: {str(e)}")
    
    def _get_image_for_condition(self, pictocode: int, windspeed: float) -> str:
        """Map meteoblue condition to specific image filenames"""
        # Priority: Wind > Rain > Cloud > Sun
        
        if windspeed > 30: # Threshold for "Windy"
            return "windy.png"
            
        # Meteoblue pictocodes (roughly)
        # 1-3: Sunny/Clear
        # 4-8: Cloudy/Overcast
        # 9-17: Rain/Snow/Fog
        # >17: Storms/Mixed
        
        if pictocode <= 3:
            return "mostly-sunny.png"
        elif pictocode <= 8:
            return "mixed-sun.png"
        else:
            return "rain.png"

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
            if "data_day" in weather_data:
                day = weather_data["data_day"]
                max_t = day.get("temperature_max", ["N/A"])[0]
                min_t = day.get("temperature_min", ["N/A"])[0]
                lines.append(f"Day Max: {max_t}°C | Day Min: {min_t}°C")

            # 3. Current Conditions
            if "data_1h" in weather_data:
                d1h = weather_data["data_1h"]
                # Index 0 is current hour
                curr_temp = d1h.get("temperature", [0])[0]
                curr_wind = d1h.get("windspeed", [0])[0]
                curr_code = d1h.get("pictocode", [1])[0]
                
                curr_img = self._get_image_for_condition(curr_code, curr_wind)
                lines.append(f"Current Temp: {curr_temp}°C")
                lines.append(f"Current Condition: {curr_img}")
                
                # 4. Hourly Forecast (Next 5 hours)
                lines.append("\nForecast (Next 5 Hours):")
                # Loop from index 1 (next hour) to 5
                for i in range(1, 6):
                    # Safety check for list length
                    if i < len(d1h.get("temperature", [])):
                        f_temp = d1h["temperature"][i]
                        f_wind = d1h["windspeed"][i]
                        f_code = d1h["pictocode"][i]
                        f_img = self._get_image_for_condition(f_code, f_wind)
                        lines.append(f"+{i}h: {f_temp}°C [{f_img}]")
            
            if not lines:
                return "No weather data available."
                
            return "\n".join(lines)

        except Exception as e:
            return f"Error formatting weather data: {str(e)}"

# Singleton instance
weather_service = WeatherService()