import asyncio
import re
import os
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    # URL of the SSE endpoint
    # Use port 8080 to test via Nginx (Auth enabled)
    # Use port 8000 to test direct Python (No Auth)
    port = os.environ.get("PORT", "8080")
    url = f"http://localhost:{port}/sse"
    
    # Auth Token (Must match .env if using Nginx)
    auth_token = os.environ.get("MCP_AUTH_TOKEN", "secret_token_change_me")
    
    print(f"Connecting to {url}...")
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        print(f"Using Auth Token: {auth_token[:5]}...")

    try:
        async with sse_client(url, headers=headers) as (read_stream, write_stream):
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
                
                # Parse coordinates
                lat_match = re.search(r"Latitude ([0-9.-]+)", geo_text)
                lng_match = re.search(r"Longitude ([0-9.-]+)", geo_text)
                
                if lat_match and lng_match:
                    lat = float(lat_match.group(1))
                    lng = float(lat_match.group(1))
                    print(f"-> Parsed: Lat={lat}, Lng={lng}")
                    
                    # 2. Test Nearby Search
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

                    # 3. Test Weather
                    print(f"\n--- 3. Testing 'get_weather' for ({lat}, {lng}) ---")
                    weather_args = {"latitude": lat, "longitude": lng}
                    print(f"Calling tool with args: {weather_args}")
                    
                    weather_result = await session.call_tool("get_weather", arguments=weather_args)
                    print("\n--- Weather Result ---")
                    for content in weather_result.content:
                        print(content.text)

                else:
                    print("\nCould not parse coordinates. Skipping dependent tests.")
                        
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Ensure the server is running via 'docker-compose up' (for port 8080) or 'fastmcp run' (for port 8000).")

    # --- Test Authentication Failure ---
    print("\n\n--- Testing Authentication Failure ---")
    wrong_token = "this_is_a_wrong_token"
    print(f"Attempting connection with INCORRECT token: {wrong_token[:5]}...")
    
    headers_fail = {"Authorization": f"Bearer {wrong_token}"}
    
    try:
        async with sse_client(url, headers=headers_fail) as (read_stream, write_stream):
            print("ERROR: Connected successfully with incorrect token. Authentication is NOT working!")
    except Exception as e:
        print(f"SUCCESS: Connection FAILED with incorrect token as expected. Error: {e}")
        # The exact exception might be ConnectError, McpError, or something else depending on the exact
        # way Nginx or the client library handles the 401 response and closes the connection.
        # The key is that it *did not connect successfully*.

if __name__ == "__main__":
    asyncio.run(main())