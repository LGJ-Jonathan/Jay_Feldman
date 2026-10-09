# Hosting the give-first desk on Bob

The desk is three files and one rule: **the page never talks to Bison or Consulti.**
It reads one JSON file that Hermes regenerates. That keeps API keys off the page
and means a browser can never trigger a send.

```
dashboard/index.html              the page. No build step, no dependencies.
dashboard/data.json               written by scripts/build-dashboard-data.py
scripts/dashboard-server.py       serves those two, and takes approvals
scripts/dashboard-decisions.json  written by the server, read by Hermes
```

## Why it is not on the internet

`data.json` carries prospect names, company names and email addresses for every
interested lead. The server **refuses to bind to anything but localhost** for that
reason. Reaching it from your phone is cloudflared's job, with Cloudflare Access in
front of the hostname so only your Google account can open it.

## Put it up

**1. Start the server** (as the Hermes user, so it can read the repo):

```bash
cd ~/LGJ/Jay_Feldman
python3 scripts/dashboard-server.py --port 8750
```

Confirm it with `curl -s localhost:8750/healthz` → `{"ok": true, "data_json": true}`.

**2. Keep it running.** A launchd plist or systemd unit is tidier, but the smallest
thing that survives a logout is:

```bash
nohup python3 scripts/dashboard-server.py --port 8750 >> ~/.hermes/desk.log 2>&1 &
```

**3. Point cloudflared at it.** Bob already runs a tunnel for
`hermes-hooks.nextwave.io`, so add a hostname to the same tunnel's config rather
than starting a second one:

```yaml
ingress:
  - hostname: hermes-hooks.nextwave.io
    service: http://127.0.0.1:8644
  - hostname: desk.nextwave.io          # the new one
    service: http://127.0.0.1:8750
  - service: http_status:404            # keep this last
```

Then `cloudflared tunnel route dns <tunnel-name> desk.nextwave.io` and restart the
tunnel.

**4. Lock it down before you open it.** In Cloudflare Zero Trust, add an Access
application for `desk.nextwave.io` with a policy allowing your email only. Do this
step before you load the page the first time. Without it, the hostname is public and
so is every lead's email address.

## Keep the data current

One command regenerates everything the page shows:

```bash
BISON_API_KEY=… python3 scripts/build-dashboard-data.py
```

It writes `data.json` atomically, so the page never reads a half-written file. The
page re-reads every 60 seconds and whenever you switch back to the tab.

Hermes should run it **after every sweep**, and on its own every 15 minutes so the
campaign counters stay fresh:

```
*/15 * * * *  cd ~/LGJ/Jay_Feldman && BISON_API_KEY=… python3 scripts/build-dashboard-data.py >> ~/.hermes/desk-data.log 2>&1
```

If Bison is unreachable, the script keeps the rest of the page correct and lists what
it could not refresh; the page shows that as a banner rather than silently showing
old numbers as current.

## What Hermes does with an approval

Approving on the page writes one entry to `scripts/dashboard-decisions.json`:

```json
{ "6970644": { "status": "approved", "at": "2026-10-09T01:35:29+00:00" } }
```

That file is the whole contract. Hermes reads it and, for each `approved` id that is
not already in `scripts/sent-log.json`:

```bash
python3 scripts/send-approved.py \
  --reply-id <id> \
  --body-file Leads/fulfillment/staged/<id>.txt \
  --attach Leads/fulfillment/lists/<the list named in data.json>
```

Every guard still runs on every send: the killswitch, the one-send-ever log, the
`automated_reply` check, the live thread re-read, the gift-code placeholder check and
the daily cap. **The page cannot bypass any of them**, because approving only writes
a line to a file.

After sending, Hermes regenerates `data.json`, and the lead moves to Sent on the page.

## The killswitch still wins

`scripts/sender.off` stops everything. The page reads its presence and shows the
sender as paused. Approvals keep queueing while it is there, and nothing goes out.

## If you would rather not host it on Bob

The page is a static file plus two JSON routes, so Cloudflare Pages with a Worker,
or any small box, works the same way. The only requirements are that whatever serves
it is behind authentication, and that something regenerates `data.json` on a
schedule. Do not put `data.json` in a public bucket.
