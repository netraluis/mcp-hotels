# Tools Directory

This directory contains the logic for individual MCP tools.

## Key Files
- `google_nearby.py`: Implements the `search_nearby` functionality using Google Places API.
    - Handles environment configuration and API calls.
    - Includes mocking support via `MOCK_GOOGLE_API`.
- `geocoding.py`: Implements the `get_coordinates` functionality using Google Geocoding API.
    - Converts addresses to latitude/longitude.
- `weather.py`: Implements the `get_weather` functionality using Meteoblue API.
    - Fetches current weather and forecast.
    - Formats data into a readable string for the LLM context.
    - Includes mocking support via `MOCK_WEATHER_API`.
- `distance.py`: Implements the `calculate_distance` functionality using Google Distance Matrix API.
    - Calculates distance and duration between two points.
    - Includes mocking support via `MOCK_GOOGLE_API`.