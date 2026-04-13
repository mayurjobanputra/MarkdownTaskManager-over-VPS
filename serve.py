#!/usr/bin/env python3
"""Kanban board HTTP server with API for remote read/write of kanban.md and archive.md.
Binds to localhost:8444 only. Supports two modes:
  - Local: open task-manager.html directly (File System Access API)
  - Remote: serve over HTTP/SSH tunnel, API handles file I/O
"""

import http.server
import json
import os

PORT = 8444
DIRECTORY = "/root/projects/kanban"


class KanbanHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/task-manager.html")
            self.end_headers()
            return
        if self.path == "/api/board":
            self._serve_file("kanban.md")
            return
        if self.path == "/api/archive":
            self._serve_file("archive.md")
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/board":
            self._save_file("kanban.md")
            return
        if self.path == "/api/archive":
            self._save_file("archive.md")
            return
        self.send_error(404)

    def _serve_file(self, filename):
        filepath = os.path.join(DIRECTORY, filename)
        try:
            with open(filepath, "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except FileNotFoundError:
            self.send_error(404, f"{filename} not found")

    def _save_file(self, filename):
        filepath = os.path.join(DIRECTORY, filename)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        with open(filepath, "w") as f:
            f.write(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Silence request logging


if __name__ == "__main__":
    with http.server.HTTPServer(("127.0.0.1", PORT), KanbanHandler) as httpd:
        print(f"Serving kanban board at http://127.0.0.1:{PORT}")
        print(f"  Local:  open http://127.0.0.1:{PORT}/task-manager.html")
        print(f"  Remote: ssh -L {PORT}:localhost:{PORT} <vps> then http://localhost:{PORT}")
        print(f"  API:    GET/POST /api/board, GET/POST /api/archive")
        httpd.serve_forever()
