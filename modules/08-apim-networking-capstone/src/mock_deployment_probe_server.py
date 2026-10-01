"""Local mock server for the Foundry BYOM deployment-metadata probe.

The teaching goal is to model the gateway behavior that Foundry expects when it
validates a BYOM connection:

    GET /deployments/{model}

with no api-version query parameter, returning an ARM Cognitive Services
deployment resource shape.
"""
from __future__ import annotations

import argparse
import json
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


def build_deployment_metadata_response(model_name: str) -> dict[str, Any]:
    """Return an ARM-shaped Cognitive Services deployment resource payload."""
    return {
        "id": (
            "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/"
            f"Microsoft.CognitiveServices/accounts/<account-name>/deployments/{model_name}"
        ),
        "name": model_name,
        "type": "Microsoft.CognitiveServices/accounts/deployments",
        "sku": {"name": "GlobalStandard", "capacity": 10},
        "properties": {
            "model": {
                "format": "OpenAI",
                "name": model_name,
                "version": "2025-01-01",
            },
            "provisioningState": "Succeeded",
            "capabilities": {
                "chatCompletion": "true",
                "responses": "true",
            },
            "raiPolicyName": "Microsoft.DefaultV2",
        },
    }


def create_server(host: str, port: int, model_name: str) -> ThreadingHTTPServer:
    """Create a local HTTP server that serves the deployment probe contract."""

    class DeploymentProbeHandler(BaseHTTPRequestHandler):
        server_version = "DeploymentProbeMock/1.0"

        def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/healthz":
                self._write_json(200, {"status": "ok"})
                return

            if parsed.path == f"/deployments/{model_name}":
                query = parse_qs(parsed.query)
                if "api-version" in query:
                    self._write_json(
                        400,
                        {
                            "error": (
                                "This teaching mock rejects api-version on GET "
                                "/deployments/{model} because the Foundry BYOM validation "
                                "probe is expected to arrive without it."
                            )
                        },
                    )
                    return

                self._write_json(200, build_deployment_metadata_response(model_name))
                return

            self._write_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), DeploymentProbeHandler)


def run_server(host: str, port: int, model_name: str) -> None:
    """Run the mock server until the process is interrupted."""
    server = create_server(host, port, model_name)
    shutdown_event = threading.Event()

    def _shutdown(*_: object) -> None:
        if shutdown_event.is_set():
            return
        shutdown_event.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _shutdown)
        except ValueError:
            pass

    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local deployment-probe mock server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on.")
    parser.add_argument(
        "--model-name",
        default="demo-model",
        help="Deployment/model name that the mock should expose.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.host, arguments.port, arguments.model_name)
