import os
import googlemaps
from typing import List, Dict, Any, Optional

def get_nearby_places(
    latitude: float,
    longitude: float,
    radius: int = 1000,
    keyword: str = "hotel",
    api_key: Optional[str] = None,
    type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    language: Optional[str] = None,
    rankby: Optional[str] = None,
    name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for nearby places using Google Maps Nearby Search API.
    
    Returns a maximum of 5 places, sorted by rating (descending).
    The API returns up to 20 results, but we limit to 5 to save credits and optimize processing.
    
    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        radius: Search radius in meters (required if rankby is not "distance").
        keyword: Keyword to search for (e.g., "hotel", "restaurant").
        api_key: Optional API key. If not provided, looks for GOOGLE_API_KEY env var.
        type: Optional specific place type (e.g., "lodging", "restaurant", "cafe").
        min_price: Optional minimum price level (0-4, where 0=free, 4=very expensive).
        max_price: Optional maximum price level (0-4, where 0=free, 4=very expensive).
        language: Optional language code for results (e.g., "es", "en", "fr").
        rankby: Optional ranking method: "distance" or "prominence". 
                If "distance", radius parameter is ignored.
        name: Optional exact name of the place to search for.
        
    Returns:
        List[Dict[str, Any]]: A list of up to 5 places, sorted by rating (descending).
        Each dictionary contains place information with fields such as:
        - name: str - Place name
        - vicinity: str - Approximate address
        - formatted_address: str - Full formatted address
        - rating: float - Average rating (1.0-5.0)
        - user_ratings_total: int - Total number of ratings
        - price_level: int - Price level (0-4)
        - place_id: str - Unique place identifier
        - geometry.location.lat/lng: float - Coordinates
        - types: List[str] - Place types/categories
        - opening_hours: dict - Opening hours information (if available)
        - photos: List[dict] - Photo references (if available)
        - business_status: str - Business status (e.g., "OPERATIONAL")
        And other optional fields depending on data availability.
    """
    
    # Check for Mocking
    mock_env = os.environ.get("MOCK_GOOGLE_API", "false").lower()
    if mock_env == "true":
        mock_places = [
            {
                "place_id": "mock_place_1",
                "name": "The Grand Mock Resort",
                "vicinity": "456 Luxury Ave, Simulation Town",
                "formatted_address": "456 Luxury Avenue, Simulation Town, ST 12345",
                "rating": 5.0,
                "user_ratings_total": 1250,
                "price_level": 4,
                "types": ["lodging", "resort", "establishment", "point_of_interest"],
                "geometry": {
                    "location": {
                        "lat": latitude - 0.001,
                        "lng": longitude - 0.001
                    }
                },
                "opening_hours": {
                    "open_now": True,
                    "weekday_text": [
                        "Monday: 9:00 AM – 11:00 PM",
                        "Tuesday: 9:00 AM – 11:00 PM",
                        "Wednesday: 9:00 AM – 11:00 PM",
                        "Thursday: 9:00 AM – 11:00 PM",
                        "Friday: 9:00 AM – 11:00 PM",
                        "Saturday: 9:00 AM – 11:00 PM",
                        "Sunday: 9:00 AM – 11:00 PM"
                    ]
                },
                "photos": [
                    {
                        "photo_reference": "mock_photo_ref_1",
                        "width": 800,
                        "height": 600
                    }
                ],
                "business_status": "OPERATIONAL"
            },
            {
                "place_id": "mock_place_2",
                "name": "Mock Hotel California",
                "vicinity": "123 Mockingbird Lane, Mock City",
                "formatted_address": "123 Mockingbird Lane, Mock City, MC 54321",
                "rating": 4.5,
                "user_ratings_total": 850,
                "price_level": 3,
                "types": ["lodging", "hotel", "establishment", "point_of_interest"],
                "geometry": {
                    "location": {
                        "lat": latitude + 0.001,
                        "lng": longitude + 0.001
                    }
                },
                "opening_hours": {
                    "open_now": True,
                    "weekday_text": [
                        "Monday: 8:00 AM – 10:00 PM",
                        "Tuesday: 8:00 AM – 10:00 PM",
                        "Wednesday: 8:00 AM – 10:00 PM",
                        "Thursday: 8:00 AM – 10:00 PM",
                        "Friday: 8:00 AM – 10:00 PM",
                        "Saturday: 8:00 AM – 10:00 PM",
                        "Sunday: 8:00 AM – 10:00 PM"
                    ]
                },
                "photos": [
                    {
                        "photo_reference": "mock_photo_ref_2",
                        "width": 800,
                        "height": 600
                    }
                ],
                "business_status": "OPERATIONAL"
            },
            {
                "place_id": "mock_place_3",
                "name": "Budget Mock Inn",
                "vicinity": "789 Economy St, Test Town",
                "formatted_address": "789 Economy Street, Test Town, TT 67890",
                "rating": 4.2,
                "user_ratings_total": 320,
                "price_level": 2,
                "types": ["lodging", "hotel", "establishment", "point_of_interest"],
                "geometry": {
                    "location": {
                        "lat": latitude + 0.002,
                        "lng": longitude + 0.002
                    }
                },
                "opening_hours": {
                    "open_now": True,
                    "weekday_text": [
                        "Monday: 7:00 AM – 9:00 PM",
                        "Tuesday: 7:00 AM – 9:00 PM",
                        "Wednesday: 7:00 AM – 9:00 PM",
                        "Thursday: 7:00 AM – 9:00 PM",
                        "Friday: 7:00 AM – 9:00 PM",
                        "Saturday: 7:00 AM – 9:00 PM",
                        "Sunday: 7:00 AM – 9:00 PM"
                    ]
                },
                "business_status": "OPERATIONAL"
            },
            {
                "place_id": "mock_place_4",
                "name": "Cozy Mock Lodge",
                "vicinity": "321 Comfort Blvd, Demo City",
                "formatted_address": "321 Comfort Boulevard, Demo City, DC 13579",
                "rating": 4.0,
                "user_ratings_total": 180,
                "price_level": 2,
                "types": ["lodging", "establishment", "point_of_interest"],
                "geometry": {
                    "location": {
                        "lat": latitude - 0.002,
                        "lng": longitude - 0.002
                    }
                },
                "opening_hours": {
                    "open_now": False,
                    "weekday_text": [
                        "Monday: 10:00 AM – 8:00 PM",
                        "Tuesday: 10:00 AM – 8:00 PM",
                        "Wednesday: 10:00 AM – 8:00 PM",
                        "Thursday: 10:00 AM – 8:00 PM",
                        "Friday: 10:00 AM – 8:00 PM",
                        "Saturday: 10:00 AM – 8:00 PM",
                        "Sunday: Closed"
                    ]
                },
                "business_status": "OPERATIONAL"
            },
            {
                "place_id": "mock_place_5",
                "name": "Basic Mock Hostel",
                "vicinity": "555 Simple Rd, Sample Village",
                "formatted_address": "555 Simple Road, Sample Village, SV 24680",
                "rating": 3.8,
                "user_ratings_total": 95,
                "price_level": 1,
                "types": ["lodging", "hostel", "establishment", "point_of_interest"],
                "geometry": {
                    "location": {
                        "lat": latitude + 0.003,
                        "lng": longitude + 0.003
                    }
                },
                "business_status": "OPERATIONAL"
            }
        ]
        
        # Sort by rating descending and limit to 5
        sorted_mock = sorted(mock_places, key=lambda x: x.get('rating', 0), reverse=True)
        return sorted_mock[:5]

    # Validate parameters
    if min_price is not None and (min_price < 0 or min_price > 4):
        raise ValueError("min_price must be between 0 and 4")
    if max_price is not None and (max_price < 0 or max_price > 4):
        raise ValueError("max_price must be between 0 and 4")
    if rankby is not None and rankby not in ["distance", "prominence"]:
        raise ValueError("rankby must be either 'distance' or 'prominence'")
    if rankby == "distance" and radius is not None:
        # If rankby is distance, radius should not be used
        radius = None

    # Real API Call
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key is required. Set GOOGLE_API_KEY env var or provide it.")

    try:
        gmaps = googlemaps.Client(key=key)
        
        # Build parameters dynamically, only including non-None values
        params = {
            "location": (latitude, longitude),
        }
        
        # Add radius only if rankby is not "distance"
        if rankby != "distance" and radius is not None:
            params["radius"] = radius
        
        if keyword:
            params["keyword"] = keyword
        
        if type:
            params["type"] = type
        
        if min_price is not None:
            params["min_price"] = min_price
        
        if max_price is not None:
            params["max_price"] = max_price
        
        if language:
            params["language"] = language
        
        if rankby:
            params["rankby"] = rankby
        
        if name:
            params["name"] = name
        
        # Call API
        results = gmaps.places_nearby(**params)
        
        # Get results list
        places = results.get('results', [])
        
        # Sort by rating (descending), handling None ratings as 0
        sorted_places = sorted(places, key=lambda x: x.get('rating', 0) or 0, reverse=True)
        
        # Limit to 5 results (API returns up to 20, but we limit to save credits)
        return sorted_places[:5]
        
    except Exception as e:
        print(f"Error querying Google Maps API: {e}")
        # Re-raise exception to alert the client of the error
        raise RuntimeError(f"Google Maps API failed: {e}")
