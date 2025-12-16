from fastmcp import FastMCP
from tools.google_nearby import get_nearby_places
from tools.geocoding import geocode_address
from tools.weather import weather_service
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
async def get_weather(latitude: float, longitude: float) -> str:
    """
    Get the current weather and forecast for a specific location (latitude/longitude).
    Returns a readable string with temperature, wind, etc.
    """
    try:
        data = await weather_service.get_weather(latitude, longitude)
        return weather_service.format_weather_for_context(data)
    except Exception as e:
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
def search_nearby(latitude: float, longitude: float, radius: int = 1000, keyword: str = "hotel") -> str:
    """
    Search for nearby places (hotels, restaurants, etc.) using Google Maps API.
    
    Args:
        latitude: Latitude of the search center.
        longitude: Longitude of the search center.
        radius: Search radius in meters (default 1000).
        keyword: Type of place to search for (default "hotel").
    """
    logger.info(f"search_nearby called: lat={latitude}, lng={longitude}, radius={radius}, keyword={keyword}")
    results = get_nearby_places(latitude, longitude, radius, keyword)
    
    # Format results as a readable string
    if not results:
        return f"No {keyword}s found near ({latitude}, {longitude})."
    
    formatted_results = [f"Found {len(results)} places:\n"]
    for place in results:
        name = place.get("name", "Unknown")
        vicinity = place.get("vicinity", "No address")
        rating = place.get("rating", "N/A")
        formatted_results.append(f"- {name} (Rating: {rating})\n  Address: {vicinity}")
        
    return "\n".join(formatted_results)

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
