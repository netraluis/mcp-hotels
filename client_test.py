import asyncio
import re
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    # URL of the SSE endpoint (ensure server is running on port 8000)
    url = "http://localhost:8000/sse"
    # url = "https://mcp-openai.netraluis.xyz/sse"
    print(f"Connecting to {url}...")
    
    try:
        async with sse_client(url) as (read_stream, write_stream):
            print("Connected to SSE stream.")
            
            async with ClientSession(read_stream, write_stream) as session:
                print("Initializing session...")
                await session.initialize()
                print("Session initialized successfully!")
                
                # List available tools
                print("\n--- Available Tools ---")
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    print(f"Tool: {tool.name}")
                    print(f"Description: {tool.description}")
                
                # 1. Test Geocoding
                target_place = "Empire State Building"
                print(f"\n--- 1. Testing 'get_coordinates' for '{target_place}' ---")
                geo_result = await session.call_tool("get_coordinates", arguments={"address": target_place})
                
                geo_text = geo_result.content[0].text
                print(f"Result: {geo_text}")
                
                # Parse coordinates from the text response for the next step
                # Expected format: "Coordinates for '...': Latitude 40.748817, Longitude -73.985428"
                lat_match = re.search(r"Latitude ([0-9.-]+)", geo_text)
                lng_match = re.search(r"Longitude ([0-9.-]+)", geo_text)
                
                if lat_match and lng_match:
                    lat = float(lat_match.group(1))
                    lng = float(lng_match.group(1))
                    print(f"-> Parsed: Lat={lat}, Lng={lng}")
                    
                    # 2. Test Nearby Search using obtained coordinates
                    print(f"\n--- 2. Testing 'search_nearby' around {target_place} ---")
                    search_args = {
                        "latitude": lat, 
                        "longitude": lng,
                        "radius": 500,
                        "keyword": "pizza"
                    }
                    print(f"Calling tool with args: {search_args}")
                    
                    search_result = await session.call_tool("search_nearby", arguments=search_args)
                    
                    print("\n--- Search Result ---")
                    for content in search_result.content:
                        print(content.text)

                    # 3. Test Weather using same coordinates
                    print(f"\n--- 3. Testing 'get_weather' for ({lat}, {lng}) ---")
                    # Ensure MOCK_WEATHER_API is true in server env if no key
                    weather_args = {
                        "latitude": lat,
                        "longitude": lng
                    }
                    print(f"Calling tool with args: {weather_args}")
                    
                    weather_result = await session.call_tool("get_weather", arguments=weather_args)
                    print("\n--- Weather Result ---")
                    for content in weather_result.content:
                        print(content.text)

                else:
                    print("\nCould not parse coordinates from response. Skipping search and weather test.")
                        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Ensure the server is running via 'fastmcp run ...' or Docker.")

if __name__ == "__main__":
    asyncio.run(main())