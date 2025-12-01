
from flask import Flask, request, send_from_directory, render_template_string, make_response
import datetime
import os
import urllib.parse
import json
import logging
from logging.handlers import RotatingFileHandler
import pathlib
from pythonjsonlogger import jsonlogger

# defaults
WEBROOT = "fake_web"   # folder tempat hasil clone disimpan
LOG_FILE = "logs/honeypot.json"
PORT = 5050

# Load optional configuration from config.json
try:
    cfg_path = pathlib.Path(__file__).parent / "config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as _f:
            _cfg = json.load(_f)
        WEBROOT = _cfg.get("webroot", WEBROOT)
        LOG_FILE = _cfg.get("honeypot_log", LOG_FILE)
        PORT = _cfg.get("port", PORT)
except Exception:
    pass

app = Flask(__name__, static_folder=WEBROOT)
os.makedirs("logs", exist_ok=True)

# setup logger with rotation
logger = logging.getLogger("webpot.honeypot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    # Use JSON formatter to keep logs structured
    handler.setFormatter(jsonlogger.JsonFormatter())
    logger.addHandler(handler)

SUSPICIOUS_PATTERNS = [
    "' OR '1'='1",
    "union select",
    "<script",
    "../",
    "wget ",
    "curl ",
    "base64",
    "sleep(",
    ";--",
    "drop table",
    "xp_cmdshell"
]

def log_event(ip, method, ua, path, params, data, raw_body, extra=""):
    event = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ip": ip,
        "method": method,
        "user_agent": ua,
        "path": path,
        "params": params,
        "data": data,
        "raw_body": raw_body,
        "extra": extra
    }
    try:
        # log as structured fields so JsonFormatter will include them
        logger.info("", extra=event)
    except Exception:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _is_safe_path(webroot: str, requested_path: str) -> bool:
    """Ensure requested_path is inside webroot (prevent path traversal).
    Returns True when safe.
    """
    try:
        base = pathlib.Path(webroot).resolve()
        target = (base / requested_path).resolve()
        return str(target).startswith(str(base))
    except Exception:
        return False

FAKE_PASSWD = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
user:x:1000:1000:honeypot:/home/user:/bin/bash
"""

# Fallback login page used when no index.html is present
FAKE_LOGIN = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Login</title>
        <style>
            body{font-family:Arial,Helvetica,sans-serif;background:#f4f6f8}
            .card{max-width:360px;margin:6% auto;padding:2rem;background:#fff;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.06)}
            input{width:100%;padding:.6rem;margin:.4rem 0}
            button{width:100%;padding:.6rem;background:#007bff;color:#fff;border:none;border-radius:4px}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Sign In</h2>
            <form method="POST" action="/">
                <label>Username</label>
                <input name="username" type="text" autocomplete="username" />
                <label>Password</label>
                <input name="password" type="password" autocomplete="current-password" />
                <button type="submit">Sign In</button>
            </form>
            <p style="font-size:.85rem;color:#666;margin-top:.75rem">If login fails, the page will return an error message.</p>
        </div>
    </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "-")
    method = request.method
    path = request.path

    params = {k: urllib.parse.unquote(v) for k, v in request.args.items()}
    data = {k: urllib.parse.unquote(v) for k, v in request.form.items()} if method == "POST" else {}
    raw_body = urllib.parse.unquote(request.get_data(as_text=True))

    # simple size limit for incoming body to avoid resource abuse
    if len(raw_body) > 10000:
        log_event(ip, method, ua, path, params, data, raw_body, "Request body too large")
        return make_response(("Request entity too large", 413))

    suspicious = ""
    combined = str(params) + str(data) + raw_body
    for p in SUSPICIOUS_PATTERNS:
        if p.lower() in combined.lower():
            suspicious = f"Suspicious payload detected: {p}"
            break

    log_event(ip, method, ua, path, params, data, raw_body, suspicious)

    if method == "POST":
        fake_response = make_response(render_template_string("<h3>Invalid username or password</h3>" + FAKE_LOGIN), 401)
        return fake_response

    index_path = os.path.join(WEBROOT, "index.html")
    try:
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return render_template_string(f.read())
    except Exception as e:
        log_event(ip, method, ua, path, params, data, raw_body, f"Error reading index.html: {e}")
        return make_response(render_template_string(FAKE_LOGIN + "<p>Server error reading page.</p>"), 500)

    return render_template_string(FAKE_LOGIN)

@app.route("/<path:filename>", methods=["GET"])
def serve_file(filename):
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "-")
    method = request.method
    path = request.path
    params = {k: urllib.parse.unquote(v) for k, v in request.args.items()}
    raw_body = urllib.parse.unquote(request.get_data(as_text=True))

    # Reject obvious traversal patterns quickly
    if ".." in filename or filename.startswith("/"):
        log_event(ip, method, ua, path, params, {}, raw_body, "Path traversal attempt")
        return make_response((FAKE_PASSWD, 400))

    # Ensure resolved path is inside WEBROOT
    if not _is_safe_path(WEBROOT, filename):
        log_event(ip, method, ua, path, params, {}, raw_body, "Unsafe path request")
        return make_response(("Not allowed", 403))

    full_path = pathlib.Path(WEBROOT) / filename
    if not full_path.exists():
        log_event(ip, method, ua, path, params, {}, raw_body, "File not found")
        return make_response(("Not Found", 404))

    log_event(ip, method, ua, path, params, {}, raw_body, "File request")
    try:
        return send_from_directory(WEBROOT, filename)
    except Exception as e:
        log_event(ip, method, ua, path, params, {}, raw_body, f"Error serving file: {e}")
        return make_response(("Internal Server Error", 500))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
