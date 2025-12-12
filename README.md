# Google Nearby Search MCP Server

A scalable, Dockerized Model Context Protocol (MCP) server written in Python. It wraps the Google Maps Nearby Search API, allowing AI agents to find places (hotels, restaurants, etc.) based on location.

## Features

- **Google Nearby Search Tool**: Find places by coordinates, radius, and keyword.
- **Mocking Support**: Disable real API calls for testing/dev using an environment variable.
- **Dockerized**: Ready for local deployment and platforms like Dokploy.
- **Scalable Structure**: Designed to easily add more tools.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google Maps API Key (Places API enabled)

## Setup

### 1. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your details:
- `GOOGLE_API_KEY`: Your Google Maps API Key.
- `MOCK_GOOGLE_API`: Set to `true` to use hardcoded responses (saves credits), `false` for real API calls.
- `TRANSPORT`: `sse` for HTTP server (Docker), `stdio` for CLI.

### 2. Local Installation (Python)

It is highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH to include src directory (Important!)
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Option 1: Run with FastMCP CLI (Recommended for SSE/HTTP)
# This handles the server setup robustly.
fastmcp run src/server.py --transport sse --host 0.0.0.0 --port 8000

# Option 2: Run the script directly (CLI/Stdio)
export TRANSPORT=stdio
python src/server.py

# Option 3: Run the script directly (SSE)
# Ensure you set PYTHONPATH first
export TRANSPORT=sse
export HOST=0.0.0.0
export PORT=8000
python src/server.py
```

### 3. Docker Deployment (Local)

Build and run using Docker Compose:

```bash
docker-compose up --build
```

The server will be available at `http://localhost:8000/sse` (depending on FastMCP default SSE path).

### 4. Dokploy Deployment

1.  Push this repository to your Git provider (GitHub, GitLab, etc.).
2.  In Dokploy, create a new **Application**.
3.  Select your repository and branch.
4.  **Build Type**: Dockerfile.
5.  **Environment Variables**: Add your `GOOGLE_API_KEY`, `MOCK_GOOGLE_API=false`, `TRANSPORT=sse`.
6.  **Port**: Map internal port `8000` to your desired external port/domain.
7.  Deploy.

## Project Structure

- `src/server.py`: Entry point. Initializes the FastMCP server.
- `src/tools/`: Contains tool implementations.
    - `google_nearby.py`: Logic for Google Places API interaction.

## Logic Flow

1.  **Request**: Agent sends a request to `search_nearby` tool with `latitude`, `longitude`, `radius`, and `keyword`.
2.  **Mock Check**: System checks `MOCK_GOOGLE_API`.
    - If `true`: Returns hardcoded fake data.
    - If `false`: Calls Google Maps API.
3.  **Response**: Formats the list of places into a human-readable string and returns it to the agent.
# mcp-hotels
