from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Optional
from urllib.parse import urlparse

import cv2
import numpy as np


class DebugVideoServer:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[bytes] = None
        self._metrics_lock = threading.Lock()
        self._latest_metrics: Optional[dict] = None
        self._server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        server = ThreadingHTTPServer((self._host, self._port), self._handler_factory())
        self._server = server
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()

    def update_frame(self, frame_bgr: np.ndarray) -> None:
        ok, encoded = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            return
        with self._frame_lock:
            self._latest_frame = encoded.tobytes()

    def update_metrics(self, payload: dict) -> None:
        normalized = _normalize_payload(payload)
        with self._metrics_lock:
            self._latest_metrics = normalized

    def _handler_factory(self):
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urlparse(self.path).path
                if path == "/health":
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"ok")
                    return
                if path == "/metrics.json":
                    with parent._metrics_lock:
                        payload = parent._latest_metrics
                    if payload is None:
                        self.send_response(204)
                        self.end_headers()
                        return
                    encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    return
                if path == "/":
                    html = _build_debug_page().encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(html)))
                    self.end_headers()
                    self.wfile.write(html)
                    return
                if path != "/frame.jpg":
                    self.send_response(404)
                    self.end_headers()
                    return
                with parent._frame_lock:
                    frame = parent._latest_frame
                if frame is None:
                    self.send_response(204)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)

            def log_message(self, format, *args):
                return None

        return Handler


def _build_debug_page() -> str:
        return """<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Vision Debug</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 16px; background: #111; color: #eee; }
            .layout { display: grid; gap: 16px; grid-template-columns: 1fr; }
            img { width: 100%; border: 1px solid #333; border-radius: 6px; background: #000; }
            pre { background: #1b1b1b; padding: 12px; border-radius: 6px; overflow: auto; }
            @media (min-width: 900px) {
                .layout { grid-template-columns: 2fr 1fr; }
            }
        </style>
    </head>
    <body>
        <h2>Vision Debug</h2>
        <div class="layout">
            <div>
                <img id="frame" src="/frame.jpg" alt="debug frame" />
            </div>
            <pre id="metrics">Loading metrics...</pre>
        </div>
        <script>
            const frame = document.getElementById('frame');
            const metrics = document.getElementById('metrics');
            function refreshFrame() {
                frame.src = '/frame.jpg?ts=' + Date.now();
            }
            async function refreshMetrics() {
                try {
                    const res = await fetch('/metrics.json?ts=' + Date.now());
                    if (res.status === 204) {
                        metrics.textContent = 'No metrics yet';
                        return;
                    }
                    const data = await res.json();
                    metrics.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    metrics.textContent = 'Metrics unavailable';
                }
            }
            setInterval(refreshFrame, 200);
            setInterval(refreshMetrics, 500);
            refreshFrame();
            refreshMetrics();
        </script>
    </body>
</html>
"""


def _normalize_payload(value):
    if isinstance(value, dict):
        return {str(k): _normalize_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_payload(item) for item in value]
    try:
        return float(value)
    except (TypeError, ValueError):
        return value
