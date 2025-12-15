import os
import googlemaps
from typing import Dict, Any, Optional, Union

def geocode_address(
    address: str,
    api_key: Optional[str] = None
) -> Union[Dict[str, float], str]:
    """
    Convert an address or place name into geographic coordinates (latitude/longitude).
    
    Args:
        address: The address or place name to geocode (e.g., "Eiffel Tower", "1600 Amphitheatre Parkway").
        api_key: Optional API key. If not provided, looks for GOOGLE_API_KEY env var.
        
    Returns:
        A dictionary with 'lat' and 'lng' keys, or an error string if not found.
    """
    
    # Check for Mocking
    mock_env = os.environ.get("MOCK_GOOGLE_API", "false").lower()
    if mock_env == "true":
        # Return a fixed mock location (e.g., roughly Central Park, NY)
        return {"lat": 40.785091, "lng": -73.968285}

    # Real API Call
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key is required. Set GOOGLE_API_KEY env var.")

    try:
        gmaps = googlemaps.Client(key=key)
        
        # Geocoding API call
        results = gmaps.geocode(address)
        
        if not results:
            return f"No coordinates found for address: '{address}'"
            
        # Extract location from the first result
        location = results[0].get('geometry', {}).get('location')
        
        if location:
            return location
        else:
            return f"Could not extract location data for: '{address}'"
        
    except Exception as e:
        print(f"Error querying Google Geocoding API: {e}")
        raise RuntimeError(f"Google Geocoding API failed: {e}")
