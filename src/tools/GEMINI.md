# Tools Directory

This directory contains the logic for individual MCP tools.

## Key Files
- `google_nearby.py`: Implements the `search_nearby` functionality. It handles:
    - Environment configuration reading.
    - Google Maps Places API interaction.
    - Mocking logic for testing (controlled by `MOCK_GOOGLE_API`).
- `geocoding.py`: Implements the `get_coordinates` functionality. It handles:
    - Google Maps Geocoding API interaction.
    - Converting addresses to latitude/longitude.
