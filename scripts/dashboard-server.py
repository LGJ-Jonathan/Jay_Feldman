#!/usr/bin/env python3
"""
Serves the give-first desk, and takes approvals from it.

Three routes and nothing else:

  GET  /                 dashboard/index.html
  GET  /data.json        whatever build-dashboard-data.py last wrote
  GET  /api/decisions    the decision map, as JSON
  POST /api/decisions    {"id": "...", "status": "approved"|"skipped"|""} and
                         writes scripts/dashboard-decisions.json
  GET  /d/<token>        one list, to one prospect, by token
  GET  /api/niche-map    consulti-niche-filter-map.json, for the workflow engine
  GET  /api/manifest     scripts/list-manifest.json, ditto
  POST /api/mint         mints a list link; needs the X-Mint-Key header

It cannot send email. Hermes reads dashboard-decisions.json to learn what was
approved, and the send still goes through scripts/send-approved.py with every
guard intact.

  python3 scripts/dashboard-server.py            # 127.0.0.1:8750
  python3 scripts/dashboard-server.py --port 9000 --host 127.0.0.1

It binds to localhost only, by design: data.json carries prospect names and
email addresses. Put cloudflared in front of it to reach it from outside, with
Cloudflare Access on the hostname. Never bind it to 0.0.0.0 on a public box.
"""
import hmac, json, os, secrets, sys, threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "dashboard"
DECISIONS = ROOT / "scripts" / "dashboard-decisions.json"
TOKENS = ROOT / "scripts" / "list-tokens.json"
LISTS = ROOT / "Leads" / "fulfillment" / "lists"
NICHE_MAP = ROOT / "consulti-niche-filter-map.json"
MANIFEST = ROOT / "scripts" / "list-manifest.json"
MINT_KEY = os.environ.get("MINT_KEY", "")
TTL_DAYS = int(os.environ.get("LIST_LINK_TTL_DAYS", "90"))
LINK_BASE = os.environ.get("LIST_LINK_BASE", "https://files.nextwave.io")
VALID = {"approved", "skipped", ""}
MAX_BODY = 4096
LOCK = threading.Lock()


def read_decisions():
    try:
        return json.loads(DECISIONS.read_text())
    except Exception:
        return {}


def write_decisions(d):
    tmp = DECISIONS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, indent=1))
    tmp.replace(DECISIONS)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "give-first-desk"

    def log_message(self, fmt, *a):
        sys.stderr.write("%s  %s\n" % (self.log_date_time_string(), fmt % a))

    def _send(self, code, body=b"", ctype="application/json", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _file(self, rel, ctype):
        p = WEB / rel
        if not p.is_file():
            self._json(404, {"error": f"{rel} is not there yet. "
                                      "Run scripts/build-dashboard-data.py."})
            return
        self._send(200, p.read_bytes(), ctype)

    def _download(self, token):
        """Serve one list to one prospect, by token. See scripts/mint-list-link.py."""
        from datetime import datetime, timezone
        try:
            db = json.loads(TOKENS.read_text())
        except Exception:
            self._send(404, b"Not found", "text/plain; charset=utf-8"); return
        rec = db.get("tokens", {}).get(token)
        if not rec or rec.get("revoked"):
            self._send(404, b"That link is not valid.", "text/plain; charset=utf-8"); return
        if rec.get("expires") and rec["expires"] < datetime.now(timezone.utc).isoformat():
            self._send(410, b"That link has expired. Reply and I'll send a fresh one.",
                       "text/plain; charset=utf-8"); return
        f = LISTS / rec["list"]
        if not f.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8"); return
        with LOCK:                      # record the fetch, capped so it cannot grow forever
            rec.setdefault("fetches", []).append(
                datetime.now(timezone.utc).isoformat(timespec="seconds"))
            rec["fetches"] = rec["fetches"][-20:]
            tmp = TOKENS.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(db, indent=1)); tmp.replace(TOKENS)
        self._send(200, f.read_bytes(), "text/csv; charset=utf-8",
                   {"Content-Disposition": f'attachment; filename="{rec["list"]}"'})

    def _authed(self):
        """The mint route is the only one that writes on behalf of a robot.

        Unset MINT_KEY closes the route rather than opening it. A missing
        secret should never mean "no auth required".
        """
        if not MINT_KEY:
            self._json(503, {"error": "MINT_KEY is not set on this server, "
                                      "so minting over HTTP is switched off"})
            return False
        if not hmac.compare_digest(self.headers.get("X-Mint-Key", ""), MINT_KEY):
            self._json(401, {"error": "bad or missing X-Mint-Key"})
            return False
        return True

    def _mint(self, payload):
        """One token per prospect per list, idempotent. Same logic as
        scripts/mint-list-link.py, reachable by the workflow engine."""
        try:
            reply_id = str(payload["reply_id"]).strip()
            name = str(payload["list"]).strip()
            email = str(payload["email"]).strip()
            rows = payload.get("rows")
        except Exception:
            self._json(400, {"error": 'send {"reply_id","list","email","rows"}'})
            return
        if not reply_id.isdigit() or not email:
            self._json(400, {"error": "reply_id must be a reply id, email must be set"})
            return
        # The name goes into a filesystem path, so it may be a bare file name only.
        if name != Path(name).name or name.startswith(".") or not name.endswith(".csv"):
            self._json(400, {"error": "list must be a bare .csv file name"})
            return
        if not (LISTS / name).is_file():
            self._json(404, {"error": f"no such list: {name}"})
            return
        now = datetime.now(timezone.utc)
        with LOCK:
            try:
                db = json.loads(TOKENS.read_text())
            except Exception:
                db = {"tokens": {}}
            for tok, rec in db["tokens"].items():
                if (rec["reply_id"] == reply_id and rec["list"] == name
                        and not rec.get("revoked")):
                    self._json(200, {"url": f"{LINK_BASE}/d/{tok}", "reused": True})
                    return
            tok = secrets.token_urlsafe(18)
            db["tokens"][tok] = {
                "reply_id": reply_id, "list": name, "email": email, "rows": rows,
                "minted": now.isoformat(timespec="seconds"),
                "expires": (now + timedelta(days=TTL_DAYS)).isoformat(timespec="seconds"),
                "fetches": [],
            }
            tmp = TOKENS.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(db, indent=1)); tmp.replace(TOKENS)
        self._json(200, {"url": f"{LINK_BASE}/d/{tok}", "reused": False})

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path.startswith("/d/"):
            self._download(path[3:]); return
        if path == "/":
            self._file("index.html", "text/html; charset=utf-8")
        elif path == "/data.json":
            self._file("data.json", "application/json")
        elif path == "/api/decisions":
            self._json(200, read_decisions())
        elif path == "/api/niche-map":
            self._send(200, NICHE_MAP.read_bytes() if NICHE_MAP.is_file() else b"{}",
                       "application/json")
        elif path == "/api/manifest":
            self._send(200, MANIFEST.read_bytes() if MANIFEST.is_file() else b"{}",
                       "application/json")
        elif path == "/healthz":
            self._json(200, {"ok": True, "data_json": (WEB / "data.json").is_file()})
        else:
            self._json(404, {"error": "no such route"})

    do_HEAD = do_GET

    def do_POST(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path not in ("/api/decisions", "/api/mint"):
            self._json(404, {"error": "no such route"})
            return
        if path == "/api/mint" and not self._authed():
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            self._json(413, {"error": "body too large"})
            return
        try:
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self._json(400, {"error": "body must be JSON"})
            return
        if path == "/api/mint":
            self._mint(payload)
            return
        try:
            rid = str(payload["id"]).strip()
            status = str(payload.get("status", "")).strip()
        except Exception:
            self._json(400, {"error": "send {\"id\": \"...\", \"status\": \"...\"}"})
            return
        if not rid.isdigit() or status not in VALID:
            self._json(400, {"error": "id must be a reply id and status one of "
                                      "approved, skipped, or empty to clear"})
            return
        with LOCK:
            d = read_decisions()
            if status:
                d[rid] = {"status": status, "at": datetime.now(timezone.utc)
                          .isoformat(timespec="seconds")}
            else:
                d.pop(rid, None)
            write_decisions(d)
            self._json(200, d)


def main():
    host = "127.0.0.1"
    port = 8750
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    if host not in ("127.0.0.1", "localhost", "::1"):
        print(f"refusing to bind {host}: data.json carries prospect contact details.\n"
              "Serve on localhost and put cloudflared with Access in front of it.",
              file=sys.stderr)
        sys.exit(2)
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"give-first desk on http://{host}:{port}  (ctrl-c to stop)")
    print(f"  page       {WEB / 'index.html'}")
    print(f"  data       {WEB / 'data.json'}")
    print(f"  decisions  {DECISIONS}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
