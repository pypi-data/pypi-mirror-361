
import asyncio
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path.cwd()))

from main import app

client = TestClient(app._app)

def handle_request(method, path, headers=None, body=None):
    headers = headers or {}
    response = client.request(method, path, headers=headers, data=body)
    return {
        "status": response.status_code,
        "headers": dict(response.headers),
        "body": response.text
    }

print("FastLoop Pyodide app initialized")
