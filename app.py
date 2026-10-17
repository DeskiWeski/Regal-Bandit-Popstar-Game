"""Cleveland Boy Adventures - tiny Flask server.

Serves the single-page game and keeps everything in ONE json file
(leaderboard.json, next to this file, or inside $DATA_DIR):
  * the global leaderboard (best scores)
  * how many players got each ending
The game itself runs 100% in the browser. If this API is unreachable the game
still plays fine and keeps a leaderboard on the player's own phone instead.
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
# Behind a proxy (PythonAnywhere, Render...) this keeps request.url_root = real https:// domain
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

DATA_FILE = Path(os.environ.get("DATA_DIR", str(BASE))) / "leaderboard.json"

# Base points per ending. Keep in sync with E[...].s in index.html.
ENDING_BASE = {
    "snitch_cold": 20, "double_agent": 45, "snitch_tape": 80, "track_flop": 15,
    "mood_ring": 30, "tim_b": 70, "justice_center": 100, "vent_stuck": 10,
    "dave": 60, "judge_fan": 85, "contempt": 25, "accordion": 95, "noise": 20,
    "parma_escape": 75, "pothole": 15,
    "boss_legend": 150, "boss_legend_snitch": 130, "grounded": 20,
}
NAME_BAD = re.compile(r"[^A-Z0-9 _.!\-]")
MAX_ENTRIES = 300      # entries kept in the file
TOP_N = 25             # entries sent to the game
SCORE_COOLDOWN = 4.0   # seconds between score posts from one IP
END_COOLDOWN = 2.0     # seconds between counted endings from one IP

_lock = threading.Lock()
_last_score = {}
_last_end = {}


def _load():
    try:
        d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            d.setdefault("entries", [])
            d.setdefault("endings", {})
            return d
    except Exception:
        pass
    return {"entries": [], "endings": {}}


def _save():
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_db, indent=1), encoding="utf-8")
        tmp.replace(DATA_FILE)
    except Exception:
        pass  # read-only disk? the board just lives in memory until restart


_db = _load()


def _int(v, lo, hi):
    try:
        n = int(v)
    except (TypeError, ValueError):
        n = lo
    return max(lo, min(hi, n))


def calc_score(ending, cred, heat, pk, snitches):
    # Same formula as calcScore() in index.html
    return ENDING_BASE[ending] + cred * 10 + pk * 5 + (10 - heat) * 3 + min(snitches, 9) * 2


def _ranked():
    return sorted(_db["entries"], key=lambda e: (-e["score"], e["ts"]))


def _top(n=TOP_N):
    return [
        {"name": e["name"], "score": e["score"], "ending": e["ending"], "snitches": e.get("snitches", 0)}
        for e in _ranked()[:n]
    ]


def _counts():
    return {"total": sum(_db["endings"].values()), "counts": _db["endings"]}


@app.after_request
def cors(resp):
    if request.path.startswith("/api/"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


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
        return jsonify(_counts())


@app.post("/api/ending")
def ending():
    body = request.get_json(silent=True) or {}
    eid = str(body.get("id", ""))
    if eid not in ENDING_BASE:
        return jsonify(error="bad id"), 400
    ip = request.remote_addr or "?"
    now = time.time()
    with _lock:
        if len(_last_end) > 5000:
            _last_end.clear()
        recent = now - _last_end.get(ip, 0) < END_COOLDOWN
        _last_end[ip] = now
        if not recent:
            _db["endings"][eid] = _db["endings"].get(eid, 0) + 1
            _save()
        return jsonify(_counts())


@app.get("/api/leaderboard")
def leaderboard():
    n = _int(request.args.get("limit", TOP_N), 1, 100)
    with _lock:
        return jsonify(entries=_top(n), total=len(_db["entries"]))


@app.post("/api/score")
def score():
    b = request.get_json(silent=True) or {}
    ending_id = str(b.get("ending", ""))
    if ending_id not in ENDING_BASE:
        return jsonify(error="bad ending"), 400
    name = NAME_BAD.sub("", str(b.get("name", "")).upper()).strip()[:12]
    if not name:
        return jsonify(error="name needed"), 400
    cred = _int(b.get("cred"), 0, 10)
    heat = _int(b.get("heat"), 0, 10)
    pk = _int(b.get("pk"), 0, 80)
    sn = _int(b.get("snitches"), 0, 9)
    sc = calc_score(ending_id, cred, heat, pk, sn)
    ip = request.remote_addr or "?"
    now = time.time()
    with _lock:
        if len(_last_score) > 5000:
            _last_score.clear()
        if now - _last_score.get(ip, 0) < SCORE_COOLDOWN:
            return jsonify(error="slow down, one score at a time"), 429
        _last_score[ip] = now
        entry = {"name": name, "score": sc, "ending": ending_id, "cred": cred, "heat": heat,
                 "pk": pk, "snitches": sn, "ts": int(now)}
        _db["entries"].append(entry)
        ranked = _ranked()
        _db["entries"] = ranked[:MAX_ENTRIES]
        rank = next((i + 1 for i, e in enumerate(ranked) if e is entry), len(ranked) + 1)
        _save()
        return jsonify(ok=True, score=sc, rank=rank, entries=_top())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_DEBUG") == "1")
