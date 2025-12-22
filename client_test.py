import asyncio
import re
import os
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# Load environment variables from .env file
load_dotenv()

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
                    lng = float(lng_match.group(1))
                    print(f"-> Parsed: Lat={lat}, Lng={lng}")
                    
                    # 2. Test Nearby Search - Basic
                    print(f"\n--- 2. Testing 'search_nearby' (basic) around {target_place} ---")
                    search_args = {
                        "latitude": lat, 
                        "longitude": lng,
                        "radius": 1000,
                        "keyword": "hotel"
                    }
                    print(f"Calling tool with args: {search_args}")
                    
                    search_result = await session.call_tool("search_nearby", arguments=search_args)
                    print("\n--- Search Result (Basic) ---")
                    for content in search_result.content:
                        print(content.text)
                    
                    # 2b. Test Nearby Search - With type parameter
                    print(f"\n--- 2b. Testing 'search_nearby' with type='lodging' ---")
                    search_args_type = {
                        "latitude": lat,
                        "longitude": lng,
                        "radius": 1000,
                        "type": "lodging"
                    }
                    print(f"Calling tool with args: {search_args_type}")
                    
                    search_result_type = await session.call_tool("search_nearby", arguments=search_args_type)
                    print("\n--- Search Result (With Type) ---")
                    for content in search_result_type.content:
                        print(content.text)
                    
                    # 2c. Test Nearby Search - With price filters
                    print(f"\n--- 2c. Testing 'search_nearby' with price filters (min_price=2, max_price=4) ---")
                    search_args_price = {
                        "latitude": lat,
                        "longitude": lng,
                        "radius": 1000,
                        "keyword": "hotel",
                        "min_price": 2,
                        "max_price": 4
                    }
                    print(f"Calling tool with args: {search_args_price}")
                    
                    search_result_price = await session.call_tool("search_nearby", arguments=search_args_price)
                    print("\n--- Search Result (With Price Filters) ---")
                    for content in search_result_price.content:
                        print(content.text)
                    
                    # 2d. Test Nearby Search - With language
                    print(f"\n--- 2d. Testing 'search_nearby' with language='es' ---")
                    search_args_lang = {
                        "latitude": lat,
                        "longitude": lng,
                        "radius": 1000,
                        "keyword": "restaurant",
                        "language": "es"
                    }
                    print(f"Calling tool with args: {search_args_lang}")
                    
                    search_result_lang = await session.call_tool("search_nearby", arguments=search_args_lang)
                    print("\n--- Search Result (With Language) ---")
                    for content in search_result_lang.content:
                        print(content.text)
                    
                    # 2e. Test Nearby Search - With rankby
                    print(f"\n--- 2e. Testing 'search_nearby' with rankby='prominence' ---")
                    search_args_rankby = {
                        "latitude": lat,
                        "longitude": lng,
                        "radius": 1000,
                        "keyword": "hotel",
                        "rankby": "prominence"
                    }
                    print(f"Calling tool with args: {search_args_rankby}")
                    
                    search_result_rankby = await session.call_tool("search_nearby", arguments=search_args_rankby)
                    print("\n--- Search Result (With Rankby) ---")
                    for content in search_result_rankby.content:
                        print(content.text)
                    
                    # 2f. Verify results limit (should always be max 5)
                    print(f"\n--- 2f. Verifying results limit (max 5) ---")
                    result_text = search_result.content[0].text
                    # Count number of results by counting numbered items
                    result_count = len(re.findall(r'^\d+\.', result_text, re.MULTILINE))
                    print(f"Number of results returned: {result_count}")
                    if result_count <= 5:
                        print("✓ SUCCESS: Results limited to 5 or less as expected")
                    else:
                        print(f"✗ ERROR: Expected max 5 results, got {result_count}")
                    
                    # 2g. Verify results are sorted by rating (descending)
                    print(f"\n--- 2g. Verifying results are sorted by rating (descending) ---")
                    # Extract ratings from result text
                    ratings = re.findall(r'Rating: ([0-9.]+)', result_text)
                    if ratings:
                        ratings_float = [float(r) for r in ratings]
                        print(f"Ratings found: {ratings_float}")
                        is_sorted = all(ratings_float[i] >= ratings_float[i+1] for i in range(len(ratings_float)-1))
                        if is_sorted:
                            print("✓ SUCCESS: Results are sorted by rating (descending)")
                        else:
                            print("✗ ERROR: Results are NOT sorted by rating (descending)")
                    else:
                        print("⚠ WARNING: Could not extract ratings from result text")

                    # 3. Test Weather
                    print(f"\n--- 3. Testing 'get_weather' for ({lat}, {lng}) ---")
                    weather_args = {"latitude": lat, "longitude": lng}
                    print(f"Calling tool with args: {weather_args}")
                    
                    weather_result = await session.call_tool("get_weather", arguments=weather_args)
                    print("\n--- Weather Result ---")
                    for content in weather_result.content:
                        print(content.text)

                    # 4. Test Distance
                    # print(f"\n--- 4. Testing 'calculate_travel_distance' ---")
                    # origin = f"{lat},{lng}" # Use previous coords
                    # destination = "Statue of Liberty, NY"
                    # print(f"Calculating from {origin} to {destination}...")
                    
                    # dist_args = {
                    #     "origin": origin,
                    #     "destination": destination,
                    #     "mode": "transit"
                    # }
                    
                    # dist_result = await session.call_tool("calculate_travel_distance", arguments=dist_args)
                    # print("\n--- Distance Result ---")
                    # for content in dist_result.content:
                    #     print(content.text)

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