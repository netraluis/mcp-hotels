# Google Nearby Search MCP Server (with Auth & Weather)

A scalable, Dockerized Model Context Protocol (MCP) server written in Python. It wraps the Google Maps APIs (Nearby Search, Geocoding) and Meteoblue Weather API, allowing AI agents to find places and check the weather.

It includes a robust **Nginx Sidecar** for Bearer Token Authentication, ensuring security without interfering with the SSE (Server-Sent Events) streaming protocol.

## Features

- **Google Nearby Search Tool**: Find places by coordinates, radius, and keyword.
- **Geocoding Tool**: Convert addresses (e.g., "Eiffel Tower") into coordinates.
- **Distance Matrix Tool**: Calculate travel time and distance between two points.
- **Weather Tool**: Get current weather and forecast via Meteoblue.
- **Authentication**: Nginx-based Bearer Token protection (Forward Auth compatible).
- **Mocking Support**: Disable real API calls for testing/dev using environment variables.
- **Dockerized**: Ready for local deployment and platforms like Dokploy.

## Prerequisites

- Python 3.11+ (for local dev)
- Docker & Docker Compose
- Google Maps API Key (Places API & Geocoding API enabled)
- Meteoblue API Key (optional, for weather)

## Setup & Configuration

### 1. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your details:

| Variable | Description |
| :--- | :--- |
| `GOOGLE_API_KEY` | Your Google Maps API Key. |
| `METEOBLUE_API_KEY` | Your Meteoblue API Key (optional). |
| `MCP_AUTH_TOKEN` | **Secret token** for Bearer Authentication (e.g., `my-secret-token`). |
| `MOCK_GOOGLE_API` | Set to `true` to use hardcoded Google responses (saves credits). |
| `MOCK_WEATHER_API` | Set to `true` to mock weather data. |
| `TRANSPORT` | `sse` for HTTP server (Docker), `stdio` for CLI. |
| `HOST` / `PORT` | Binding configuration (default 0.0.0.0:8000). |

## Architecture

This project uses a **Sidecar Pattern** for authentication:

1.  **Nginx (Port 8080):** Public entry point. Handles SSL (if configured) and **Bearer Token Authentication**. If the token is valid, it proxies the request to the Python backend.
2.  **Python MCP Server (Port 8000):** Internal logic. Handles MCP protocol, Tools, and API calls. It runs without authentication logic to ensure SSE stability.

## Running the Project

### Option A: Docker Deployment (Recommended with Auth)

This runs the full stack: Nginx (Auth) + Python (Logic).

1.  Build and start the containers:
    ```bash
    docker-compose up --build -d
    ```

2.  Access the SSE endpoint at **Port 8080**:
    *   **URL:** `http://localhost:8080/sse`
    *   **Auth:** Required. Send header `Authorization: Bearer <MCP_AUTH_TOKEN>` or URL param `?token=<MCP_AUTH_TOKEN>`.

3.  Test with the client script:
    ```bash
    # Ensure local python env is set
    source venv/bin/activate 
    export MCP_AUTH_TOKEN=your_token_from_env
    python client_test.py
    ```

### Option B: Local Python Dev (No Auth)

Run only the Python backend directly. This skips Nginx, so **authentication is disabled**.

1.  Create virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  Run server:
    ```bash
    export PYTHONPATH=$(pwd)/src
    fastmcp run src/server.py --transport sse --host 0.0.0.0 --port 8000
    ```

3.  Access at `http://localhost:8000/sse`.

## Project Structure

- `src/server.py`: Entry point. Initializes FastMCP.
- `src/tools/`:
    - `google_nearby.py`: Google Places API logic.
    - `geocoding.py`: Address to coordinates logic.
    - `weather.py`: Meteoblue weather logic.
- `nginx/`:
    - `nginx.conf.template`: Nginx configuration template with Auth logic.
- `docker-compose.yml`: Orchestration for Python + Nginx.

## Dokploy Deployment

1.  Push this repository to your Git provider.
2.  In Dokploy, create a new **Application** (Docker Compose).
3.  Set the Environment Variables in Dokploy (`GOOGLE_API_KEY`, `MCP_AUTH_TOKEN`, etc.).
4.  **Important:** Map the external port (e.g., domain) to internal container port **8080** (Nginx), NOT 8000.