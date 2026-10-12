#!/usr/bin/env python3
"""
Custom HTTP media server with Range request support for seamless video/audio seeking.
Serves the Video Pilot Pipeline media dashboard on port 8088.
"""
import os
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

PORT = 8088
PROJ_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/ebb9330c-b49f-4fbc-930b-c1c2129f2704")
VIDEO_DIR = PROJ_ROOT / "video"
AUDIO_DIR = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle" / "audio"

mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("audio/wav", ".wav")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/vtt", ".vtt")

class MediaRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range, Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        url_path = urllib.parse.unquote(self.path.split("?")[0])

        if url_path == "/" or url_path == "/index.html":
            self.serve_dashboard()
            return

        # Resolve routes
        file_path = None
        if url_path.startswith("/video/"):
            file_path = VIDEO_DIR / url_path[7:]
        elif url_path.startswith("/audio/"):
            file_path = AUDIO_DIR / url_path[7:]
        elif url_path.startswith("/artifact/"):
            file_path = ARTIFACT_DIR / url_path[10:]
        else:
            # Check relative to PROJ_ROOT
            candidate = PROJ_ROOT / url_path.lstrip("/")
            if candidate.is_file():
                file_path = candidate

        if file_path and file_path.is_file():
            self.serve_file_with_range(file_path)
        else:
            self.send_error(404, f"File Not Found: {url_path}")

    def serve_file_with_range(self, path: Path):
        file_size = path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(path))
        mime_type = mime_type or "application/octet-stream"

        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes="):
            byte_range = range_header[6:].split("-")
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1
            if end >= file_size:
                end = file_size - 1
            content_length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(content_length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(path, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(content_length))
        else:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)

    def serve_dashboard(self):
        # Read the main comparison review html if it exists, or generate dashboard
        review_html_path = ARTIFACT_DIR / "ch1_voice_comparison_review.html"
        if review_html_path.exists():
            html_bytes = review_html_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
        else:
            self.send_error(500, "Review HTML not found")

def run():
    server = HTTPServer(("0.0.0.0", PORT), MediaRequestHandler)
    print(f"Media Server running on http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
