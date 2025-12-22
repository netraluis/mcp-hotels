from fastmcp import FastMCP
from tools.google_nearby import get_nearby_places
from tools.geocoding import geocode_address
from tools.weather import weather_service
from tools.distance import calculate_distance
from typing import Optional
import os
import logging # Mantener para logs generales del servidor

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize FastMCP server
mcp = FastMCP(
    name="Google Nearby Search MCP",
    version="1.0.0",
    debug=True,
    strict_input_validation=False  # Disable strict validation to avoid parameter issues
)

# --- OLD AUTHENTICATION MIDDLEWARE REMOVED ---
# La clase ASGIAuthMiddleware y su registro han sido eliminados.

@mcp.tool()
def calculate_travel_distance(origin: str, destination: str, mode: str = "driving") -> str:
    """
    Calculate the travel distance and time between two points (addresses or coordinates).
    Modes: "driving", "walking", "bicycling", "transit".
    """
    logger.info(f"Calculating distance from '{origin}' to '{destination}' via {mode}")
    return calculate_distance(origin, destination, mode)

@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> str:
    """
    Get the current weather and forecast for a specific location (latitude/longitude).
    Returns a readable string with temperature, wind, etc.
    """
    logger.info(f"get_weather called with: lat={latitude}, lng={longitude}")
    try:
        data = await weather_service.get_weather(latitude, longitude)
        return weather_service.format_weather_for_context(data)
    except Exception as e:
        logger.error(f"get_weather error: {e}")
        return f"Failed to get weather: {e}"

@mcp.tool()
def get_coordinates(address: str) -> str:
    """
    Convert an address or place name (e.g., "Eiffel Tower", "New York City") into latitude and longitude coordinates.
    Use this tool BEFORE searching for nearby places if you only have a name/address.
    """
    result = geocode_address(address)
    
    if isinstance(result, dict):
        return f"Coordinates for '{address}': Latitude {result['lat']}, Longitude {result['lng']}"
    else:
        return str(result)

@mcp.tool()
def search_nearby(
    latitude: float,
    longitude: float,
    radius: int = 1000,
    keyword: str = "hotel",
    type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    language: Optional[str] = None,
    rankby: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Search for nearby places (hotels, restaurants, etc.) using Google Maps API.
    Returns up to 5 results, sorted by rating (descending).
    
    Args:
        latitude: Latitude of the search center.
        longitude: Longitude of the search center.
        radius: Search radius in meters (default 1000, ignored if rankby="distance").
        keyword: Type of place to search for (default "hotel").
        type: Optional specific place type (e.g., "lodging", "restaurant", "cafe").
        min_price: Optional minimum price level (0-4, where 0=free, 4=very expensive).
        max_price: Optional maximum price level (0-4, where 0=free, 4=very expensive).
        language: Optional language code for results (e.g., "es", "en", "fr").
        rankby: Optional ranking method: "distance" or "prominence" (if "distance", radius is ignored).
        name: Optional exact name of the place to search for.
    """
    logger.info(f"search_nearby called: lat={latitude}, lng={longitude}, radius={radius}, keyword={keyword}, type={type}, min_price={min_price}, max_price={max_price}, language={language}, rankby={rankby}, name={name}")
    
    results = get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        keyword=keyword,
        type=type,
        min_price=min_price,
        max_price=max_price,
        language=language,
        rankby=rankby,
        name=name
    )
    
    # Format results as a readable string
    if not results:
        search_term = keyword or type or "places"
        return f"No {search_term} found near ({latitude}, {longitude})."
    
    formatted_results = [f"Found {len(results)} places (showing top 5 by rating):\n"]
    for idx, place in enumerate(results, 1):
        name = place.get("name", "Unknown")
        vicinity = place.get("vicinity", place.get("formatted_address", "No address"))
        rating = place.get("rating", "N/A")
        user_ratings_total = place.get("user_ratings_total")
        price_level = place.get("price_level")
        place_id = place.get("place_id", "")
        business_status = place.get("business_status", "")
        photo_url = place.get("photo_url", "")
        
        # Format price level with clear dollar signs
        price_str = ""
        if price_level is not None:
            # Price levels: 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive
            price_display = {
                0: "Free",
                1: "$ (Inexpensive)",
                2: "$$ (Moderate)",
                3: "$$$ (Expensive)",
                4: "$$$$ (Very Expensive)"
            }
            price_str = f" | Price: {price_display.get(price_level, 'N/A')}"
        
        # Format ratings
        ratings_str = f"Rating: {rating}"
        if user_ratings_total:
            ratings_str += f" ({user_ratings_total} reviews)"
        
        # Format business status
        status_str = ""
        if business_status:
            status_str = f" | Status: {business_status}"
        
        formatted_results.append(
            f"{idx}. {name}\n"
            f"   {ratings_str}{price_str}{status_str}\n"
            f"   Address: {vicinity}"
        )
        if photo_url:
            formatted_results.append(f"   Photo: {photo_url}")
        if place_id:
            formatted_results.append(f"   Place ID: {place_id}")
        formatted_results.append("")  # Empty line between places
        
    return "\n".join(formatted_results).strip()

logger.info("Tool 'search_nearby' registered successfully")

if __name__ == "__main__":
    transport_mode = os.environ.get("TRANSPORT", "sse").lower()
    
    logger.info(f"Starting MCP Server with transport: {transport_mode}")
    logger.info(f"Environment variables:")
    logger.info(f"  TRANSPORT={transport_mode}")
    logger.info(f"  HOST={os.environ.get('HOST', '0.0.0.0')}")
    logger.info(f"  PORT={os.environ.get('PORT', '8000')}")
    
    try:
        if transport_mode == "sse":
            host = os.environ.get("HOST", "0.0.0.0")
            port = int(os.environ.get("PORT", "8000"))
            logger.info(f"Starting SSE server on {host}:{port}")
            logger.info(f"SSE endpoint will be available at: http://{host}:{port}/sse")
            mcp.run(transport="sse", host=host, port=port)
        else:
            logger.info("Starting stdio server")
            mcp.run()
    except Exception as e:
        import traceback
        logger.error(f"Server crashed: {e}")
        traceback.print_exc()
        raise
