"""Regal Bandit Popstar - tiny Flask server.

Serves the single-page game and keeps a global "what ending did people get"
counter so players can see how they compare to everyone else.
The game itself is 100% client-side: if the API is unreachable the game still
plays fine (the stats line just doesn't show up).
"""
import json
import os
import re
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, make_response, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

BASE = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)  # everything lives in this one folder
# Render / Heroku / PythonAnywhere sit behind a proxy; this makes request.url_root
# use the real https:// domain (needed for the link-preview image in texts).
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

DATA_FILE = Path(os.environ.get("DATA_DIR", str(BASE))) / "stats.json"
ID_RE = re.compile(r"^[a-z0-9_]{1,32}$")
MAX_IDS = 40          # never track more than this many distinct ending ids
POST_COOLDOWN = 2.0   # seconds between counted plays from one IP

_lock = threading.Lock()
_last_post = {}


def _load():
    try:
        data = json.loads(DATA_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(data):
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data))
        tmp.replace(DATA_FILE)
    except Exception:
        # Read-only or ephemeral disk? Counts just live in memory then.
        pass


_counts = _load()


def _payload():
    return {"total": sum(_counts.values()), "counts": _counts}


@app.get("/")
def index():
    html = (BASE / "index.html").read_text(encoding="utf-8")
    html = html.replace("__ORIGIN__", request.url_root.rstrip("/"))
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/og.png")
def og_image():
    return send_from_directory(BASE, "og.png", max_age=3600)


@app.get("/healthz")
def healthz():
    return "ok", 200


@app.get("/api/stats")
def stats():
    with _lock:
        return jsonify(_payload())


@app.post("/api/ending")
def ending():
    body = request.get_json(silent=True) or {}
    eid = str(body.get("id", ""))
    if not ID_RE.match(eid):
        return jsonify(error="bad id"), 400
    ip = request.remote_addr or "?"
    now = time.time()
    with _lock:
        if len(_last_post) > 5000:
            _last_post.clear()
        recent = now - _last_post.get(ip, 0) < POST_COOLDOWN
        _last_post[ip] = now
        if not recent and (eid in _counts or len(_counts) < MAX_IDS):
            _counts[eid] = _counts.get(eid, 0) + 1
            _save(_counts)
        return jsonify(_payload())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
