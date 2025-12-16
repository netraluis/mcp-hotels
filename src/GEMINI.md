# Source Directory

This directory contains the application source code.

## Key Files
- `server.py`: The entry point for the MCP server.
    - Initializes the FastMCP application.
    - Registers tools (`search_nearby`, `get_coordinates`, `get_weather`).
    - Configures the server transport (SSE/Stdio).
    - Note: Authentication logic has been moved to the Nginx sidecar to ensure SSE stability.
- `tools/`: A package containing the specific tool implementations.