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

            # Write requirements.txt
            (temp_path / "requirements.txt").write_text("fastloop\nfastapi\npydantic\n")

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
"""
