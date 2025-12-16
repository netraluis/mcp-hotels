# Nginx Configuration Directory

This directory contains configuration for the Nginx Sidecar Proxy used for authentication.

## Key Files
- `nginx.conf.template`: The template file used to generate the final `nginx.conf` inside the container.
    - It uses `envsubst` to inject the `MCP_AUTH_TOKEN` environment variable.
    - It implements simple Bearer Token validation logic.
    - It proxies valid requests to the `mcp-server` service on port 8000.
    - It is configured to support Server-Sent Events (SSE) by disabling buffering.
