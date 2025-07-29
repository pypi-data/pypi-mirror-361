# jsweb/static.py

import os
import mimetypes

def serve_static(path):
    full_path = os.path.join("static", path.lstrip("/"))

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return b"404 Not Found", "404 Not Found", [("Content-Type", "text/plain")]

    with open(full_path, "rb") as f:
        content = f.read()

    content_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
    return content, "200 OK", [("Content-Type", content_type)]
