import tempfile
import zipfile
from pathlib import Path
from typing import Any


class FastLoopCompiler:
    def __init__(self):
        self.default_config = {
            "debug_mode": False,
            "log_level": "INFO",
            "state": {"type": "memory"},
        }

    def compile_to_pyodide_bundle(
        self, source_code: str, config: dict[str, Any] | None = None
    ) -> bytes:
        """
        Package FastLoop source code into a Pyodide-compatible zip bundle.
        """
        final_config = self.default_config.copy()
        if config:
            final_config.update(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write your FastLoop app
            (temp_path / "main.py").write_text(source_code)

            # Write config file
            import yaml

            yaml.dump(final_config, (temp_path / "config.yaml").open("w"))

            # Write entry point for Pyodide
            (temp_path / "entry.py").write_text(self._create_entry_point())

            # Write requirements.txt - use Pyodide-compatible versions
            (temp_path / "requirements.txt").write_text(
                "fastapi\npydantic>=2.0,<2.5\nPyYAML\ncloudpickle\n"
            )

            # Create zip bundle in a separate temporary location to avoid nesting
            with tempfile.NamedTemporaryFile(
                suffix=".zip", delete=False
            ) as bundle_file:
                bundle_path = Path(bundle_file.name)
                with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in temp_path.rglob("*"):
                        if file_path.is_file():
                            zipf.write(file_path, file_path.relative_to(temp_path))

                # Read the bundle bytes
                bundle_bytes = bundle_path.read_bytes()

            # Clean up the temporary zip file
            bundle_path.unlink()

            return bundle_bytes

    def _create_entry_point(self) -> str:
        return """
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

print("Loading FastLoop app...")

# Force memory state for Pyodide
def is_pyodide() -> bool:
    try:
        import sys
        return "pyodide" in sys.modules
    except ImportError:
        return False

if is_pyodide():
    print(" Pyodide detected - forcing memory state")
    # Override the config to use memory state
    import yaml
    config = yaml.safe_load(open("config.yaml"))
    config["state"] = {"type": "memory"}
    with open("config.yaml", "w") as f:
        yaml.dump(config, f)
    print("✅ Config updated to use memory state")

try:
    from main import app
    print("✅ FastLoop app imported successfully")
except Exception as e:
    print(f"❌ Error importing FastLoop app: {e}")
    import traceback
    traceback.print_exc()
    raise

# Get the ASGI app
asgi_app = app._app
print("✅ ASGI app created")

# Create a simple request handler that actually calls your FastLoop app
async def handle_request_async(method, path, headers=None, body=None):
    print(f"🔍 Handling request: {method} {path}")
    print(f"🔍 Headers: {headers}")
    print(f"🔍 Body: {body}")
    
    from starlette.requests import Request
    from starlette.responses import Response
    
    # Create scope for the request
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [(k.encode(), v.encode()) for k, v in (headers or {}).items()],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
        "server": ("127.0.0.1", 8000),
    }
    
    print(f"🔍 Scope: {scope}")
    
    # Create request
    request = Request(scope)
    if body:
        request._body = body.encode() if isinstance(body, str) else body
    
    # Create a simple response collector
    response_body = []
    response_status = 200
    response_headers = {}
    
    async def receive():
        return {"type": "http.request", "body": request._body or b""}
    
    async def send(message):
        nonlocal response_status, response_headers
        print(f"🔍 ASGI message: {message}")
        if message["type"] == "http.response.start":
            response_status = message["status"]
            response_headers = dict(message.get("headers", []))
        elif message["type"] == "http.response.body":
            response_body.append(message.get("body", b""))

    # Call the ASGI app
    try:
        print("🔍 Calling ASGI app...")
        await asgi_app(scope, receive, send)
        print("✅ ASGI app completed")

        # Combine response body
        full_body = b"".join(response_body)

        result = {
            "status": response_status,
            "headers": response_headers,
            "body": full_body.decode() if isinstance(full_body, bytes) else str(full_body)
        }
        print(f"🔍 Returning result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in ASGI app: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

# Sync wrapper for the async function
def handle_request(method, path, headers=None, body=None):
    print(f"🚀 handle_request called with: {method} {path}")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(handle_request_async(method, path, headers, body))
        print(f"🚀 handle_request returning: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in handle_request: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

print("✅ FastLoop Pyodide app initialized")
"""
