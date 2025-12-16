# Root Directory

This directory contains the main configuration and setup for the Google Nearby Search MCP Server.

## Key Files
- `Dockerfile`: Configuration for building the Docker image of the Python MCP server.
- `docker-compose.yml`: Local Docker orchestration. Defines two services:
    - `mcp-server`: The Python logic backend (Port 8000).
    - `auth-proxy`: Nginx sidecar for Bearer Token authentication (Port 8080).
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation and setup guide.
- `client_test.py`: Test script to verify connection and tools.
- `src/`: Source code directory.
- `nginx/`: Nginx configuration for the sidecar proxy.