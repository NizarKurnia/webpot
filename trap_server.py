from flask import Flask, request, send_from_directory, render_template_string, make_response
import datetime
import os
import urllib.parse
import json

WEBROOT = "fake_web"   # folder tempat hasil clone disimpan
LOG_FILE = "logs/honeypot.json"  # ganti ke JSON agar lebih terstruktur

app = Flask(__name__, static_folder=WEBROOT)
os.makedirs("logs", exist_ok=True)

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
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "ip": ip,
        "method": method,
        "user_agent": ua,
        "path": path,
        "params": params,
        "data": data,
        "raw_body": raw_body,
        "extra": extra
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

FAKE_LOGIN = """
<html>
<head><title>Login</title></head>
<body>
<h2>Admin Login</h2>
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <input type="submit" value="Login">
</form>
</body>
</html>
"""

FAKE_PASSWD = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
user:x:1000:1000:honeypot:/home/user:/bin/bash
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
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return render_template_string(f.read())

    return render_template_string(FAKE_LOGIN)

@app.route("/<path:filename>", methods=["GET"])
def serve_file(filename):
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "-")
    method = request.method
    path = request.path
    params = {k: urllib.parse.unquote(v) for k, v in request.args.items()}
    raw_body = urllib.parse.unquote(request.get_data(as_text=True))

    if "../" in filename:
        log_event(ip, method, ua, path, params, {}, raw_body, "Path traversal attempt")
        return FAKE_PASSWD, 200

    log_event(ip, method, ua, path, params, {}, raw_body, "File request")
    return send_from_directory(WEBROOT, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
