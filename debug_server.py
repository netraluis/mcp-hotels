#!/usr/bin/env python3
"""
Script de debugging para verificar que el servidor MCP esté funcionando correctamente.
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import httpx

async def test_sse_endpoint(url: str):
    """Test básico del endpoint SSE"""
    print(f"\n1. Testing SSE endpoint: {url}")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # FastMCP SSE endpoint debería estar en /sse
            response = await client.get(url)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            if response.status_code != 200:
                print(f"   Response body: {response.text[:500]}")
            return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

async def test_mcp_session(url: str):
    """Test completo de la sesión MCP"""
    print(f"\n2. Testing MCP Session: {url}")
    try:
        async with sse_client(url) as (read_stream, write_stream):
            print("   ✓ Connected to SSE stream")
            
            async with ClientSession(read_stream, write_stream) as session:
                print("   ✓ Session created")
                
                # Initialize
                print("   Initializing session...")
                await session.initialize()
                print("   ✓ Session initialized")
                
                # List tools
                print("   Listing tools...")
                tools_result = await session.list_tools()
                print(f"   ✓ Found {len(tools_result.tools)} tools:")
                
                for tool in tools_result.tools:
                    print(f"      - {tool.name}")
                    print(f"        Description: {tool.description}")
                    if hasattr(tool, 'inputSchema'):
                        print(f"        Schema: {tool.inputSchema}")
                
                return len(tools_result.tools) > 0
                
    except Exception as e:
        import traceback
        print(f"   ERROR: {e}")
        traceback.print_exc()
        return False

async def main():
    # URL del servidor (ajusta según tu configuración)
    base_url = os.environ.get("MCP_URL", "http://localhost:8000")
    sse_url = f"{base_url}/sse"
    
    print("=" * 60)
    print("MCP Server Debugging Tool")
    print("=" * 60)
    
    # Test 1: Endpoint básico
    endpoint_ok = await test_sse_endpoint(sse_url)
    
    if not endpoint_ok:
        print("\n❌ SSE endpoint no responde correctamente")
        print("\nPosibles causas:")
        print("  1. El servidor no está corriendo")
        print("  2. El puerto está incorrecto")
        print("  3. El endpoint SSE no está en /sse")
        print("  4. Hay un firewall bloqueando la conexión")
        return
    
    # Test 2: Sesión MCP completa
    session_ok = await test_mcp_session(sse_url)
    
    if session_ok:
        print("\n✅ Servidor MCP funcionando correctamente")
    else:
        print("\n❌ Error al inicializar sesión MCP o listar herramientas")
        print("\nPosibles causas:")
        print("  1. Las herramientas no están registradas correctamente")
        print("  2. Hay un error en el código del servidor")
        print("  3. El servidor no está usando el transporte SSE correctamente")

if __name__ == "__main__":
    asyncio.run(main())

