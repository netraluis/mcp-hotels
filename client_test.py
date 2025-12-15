import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    # URL of the SSE endpoint (ensure server is running on port 8000)
    url = "http://localhost:8000/sse"
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
                    print(f"Schema: {tool.inputSchema}")
                
                # Test the 'search_nearby' tool
                print("\n--- Testing 'search_nearby' Tool (Mock Mode) ---")
                # Ensure MOCK_GOOGLE_API is true in your server env for this to work without credits
                args = {
                    "latitude": 42.55192485018038, 
                    "longitude": 1.5123403642939872,
                    "radius": 500,
                    "keyword": "restaurant"
                }
                print(f"Calling tool with args: {args}")
                result = await session.call_tool("search_nearby", arguments=args)
                
                print("\n--- Tool Result ---")
                # content is a list of TextContent or ImageContent
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
                        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Ensure the server is running via 'fastmcp run ...' or Docker.")

if __name__ == "__main__":
    asyncio.run(main())
