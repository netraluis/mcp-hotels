import os
import googlemaps
from typing import Dict, Any, Optional, Union

def calculate_distance(
    origin: str,
    destination: str,
    mode: str = "driving",
    api_key: Optional[str] = None
) -> str:
    """
    Calculate the distance and travel time between two points using Google Maps.
    
    Args:
        origin: Starting point (address, place name, or "lat,lng").
        destination: End point (address, place name, or "lat,lng").
        mode: Travel mode ("driving", "walking", "bicycling", "transit").
        api_key: Optional API key.
        
    Returns:
        A readable string with distance and duration, or an error message.
    """
    
    # Check for Mocking
    mock_env = os.environ.get("MOCK_GOOGLE_API", "false").lower()
    if mock_env == "true":
        return f"Mock Distance: 5.2 km (Time: 15 mins) via {mode} from '{origin}' to '{destination}'"

    # Real API Call
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key is required. Set GOOGLE_API_KEY env var.")

    try:
        gmaps = googlemaps.Client(key=key)
        
        # Distance Matrix API call
        # It handles converting addresses/names to coords automatically
        result = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode=mode
        )
        
        # Parse result
        if result['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                dist_text = element['distance']['text']
                duration_text = element['duration']['text']
                return f"Distance: {dist_text}, Duration: {duration_text} (Mode: {mode})"
            else:
                return f"Could not calculate distance: {element['status']}"
        else:
            return f"Error from Google API: {result['status']}"
        
    except Exception as e:
        print(f"Error querying Google Distance Matrix API: {e}")
        raise RuntimeError(f"Google Distance Matrix API failed: {e}")
