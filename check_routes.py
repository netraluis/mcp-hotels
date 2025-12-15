from fastmcp import FastMCP
# Importamos mcp del módulo server. 
# Asegúrate de tener PYTHONPATH configurado o ejecutar esto desde la raíz
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from server import mcp

print("\n--- Rutas expuestas por FastMCP ---")
if hasattr(mcp, '_http_app'):
    for route in mcp._http_app.routes:
        methods = getattr(route, 'methods', 'ALL')
        print(f"Ruta: {route.path} | Métodos: {methods}")
else:
    print("No se pudo acceder a _http_app. La versión de fastmcp podría ser distinta.")

