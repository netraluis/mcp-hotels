from fastmcp import FastMCP
from tools.google_nearby import get_nearby_places
import os

# Initialize FastMCP server
mcp = FastMCP("Google Nearby Search MCP", cors_allow_origins=["*"])

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

if __name__ == "__main__":
    # Determine transport mode from environment
    # 'sse' for Docker/Web (Dokploy), 'stdio' for CLI/Local agents
    transport_mode = os.environ.get("TRANSPORT", "stdio").lower()
    
    print(f"Starting MCP Server with transport: {transport_mode}")
    
    try:
        if transport_mode == "sse":
            host = os.environ.get("HOST", "0.0.0.0")
            port = int(os.environ.get("PORT", "8000"))
            # Run as an SSE server
            mcp.run(transport="sse", host=host, port=port)
        else:
            # Default to stdio
            mcp.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Server crashed: {e}")
