import os
import googlemaps
from typing import List, Dict, Any, Optional

def get_nearby_places(
    latitude: float,
    longitude: float,
    radius: int = 1000,
    keyword: str = "hotel",
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for nearby places using Google Maps Nearby Search API.
    
    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        radius: Search radius in meters.
        keyword: Keyword to search for (e.g., "hotel", "restaurant").
        api_key: Optional API key. If not provided, looks for GOOGLE_API_KEY env var.
        
    Returns:
        A list of found places or a hardcoded mock response if MOCK_GOOGLE_API is true.
    """
    
    # Check for Mocking
    mock_env = os.environ.get("MOCK_GOOGLE_API", "false").lower()
    if mock_env == "true":
        return [
            {
                "name": "Mock Hotel California",
                "vicinity": "123 Mockingbird Lane, Mock City",
                "rating": 4.5,
                "types": ["lodging", "hotel"],
                "geometry": {
                    "location": {
                        "lat": latitude + 0.001,
                        "lng": longitude + 0.001
                    }
                }
            },
            {
                "name": "The Grand Mock Resort",
                "vicinity": "456 Fake St, Simulation Town",
                "rating": 5.0,
                "types": ["lodging", "resort"],
                "geometry": {
                    "location": {
                        "lat": latitude - 0.001,
                        "lng": longitude - 0.001
                    }
                }
            }
        ]

    # Real API Call
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key is required. Set GOOGLE_API_KEY env var or provide it.")

    try:
        gmaps = googlemaps.Client(key=key)
        
        # places_nearby parameters: location (lat, lng), radius (meters), keyword
        results = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            keyword=keyword
        )
        
        return results.get('results', [])
        
    except Exception as e:
        print(f"Error querying Google Maps API: {e}")
        # Re-raise exception to alert the client of the error
        raise RuntimeError(f"Google Maps API failed: {e}")
