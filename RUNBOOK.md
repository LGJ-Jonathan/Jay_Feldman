# Give-first fulfilment — runbook

What keeps this lane running, in the order it has to happen. Each step says who
does it and roughly how long. Anything marked **you** is something the harness
will not let me do from this session: sending prospect email, pushing to the
remote, editing permission settings, or reaching Bob over SSH.

Status as of 2026-10-08: **nothing has been emailed yet.** 23 replies are staged
and waiting, 6 are held for a human, 30 threads were answered by the old bot
before we reached them.

---

## 1. Start Tailscale on the Mac — **you**, 1 minute

The daemon is stopped, which is why the Hermes agent on Bob cannot read this
machine and why its SSH attempts time out.

```
Tailscale menu bar icon → Connect
```

Check it took:

```bash
tailscale status | head -3
```

Everything in step 5 depends on this.

---

## 2. Send the 23 staged replies — **you**, 10 minutes

This is the one that actually delivers lists. Read them first:

```bash
cd "/Users/shararamirez/Desktop/LGJ Clients/Jay_Feldman"
open Leads/fulfillment/REVIEW-2026-10-08.txt
```

Then prove the batch without sending anything:

```bash
export BISON_API_KEY='<the Consulti workspace key>'
bash scripts/send-batch.sh ready --dry-run
```

Expect 23 lines, each naming the recipient and the attachment, and a final
`sent: 0   refused: 0`. If anything says `refused`, read its reason and stop.

Send one by itself first:

```bash
python3 scripts/send-approved.py --reply-id 6970644 \
  --body-file Leads/fulfillment/staged/6970644.txt \
  --attach Leads/fulfillment/lists/manufacturing-companies.csv
```

Open that thread in Bison and confirm the CSV attached and the body reads right.
**Only then** release the rest:

```bash
bash scripts/send-batch.sh ready
```

About 8 minutes, 20 seconds apart. Ron is skipped automatically once he is in
`scripts/sent-log.json`; no reply can ever be sent twice.

Put the safety back on when you are done for the day:

```bash
touch scripts/sender.off
```

---

## 3. Replace the reply agent — **you**, 10 minutes

The agent live on these campaigns is configured for campaigns 1008 and 1009 and
answers people with a link to the prebuilt lists page. That is not what these
leads were promised, and it has already reached 30 of them.

1. **Turn the existing agent off** on 1298, 1313, 1315 and 1145. Do this first.
   Two agents on one thread is worse than none.
2. Create the new one from `consulti-give-first-reply-agent.md`:
   - Tone **Friendly**, length **Concise**
   - Knowledge base ← the PASTE-READY KNOWLEDGE BASE block
   - Scenarios ← the PASTE-READY QUESTIONS AND ANSWERS block
3. Attach it to those four campaigns only.
4. Decide where a handed-off thread lands (your inbox, a Bison tag, the desk).
   Five of the eighteen scenarios end in a hand-off and go quiet otherwise.

---

## 4. Push the repo — **you**, 1 minute

Everything below, and the Bob agent reading the sequences, needs this.

```bash
git push origin main
```

---

## 5. Put the desk on Bob — **you**, 20 minutes

Full detail in `dashboard/README.md`. Short version, run on Bob:

```bash
cd ~/LGJ/Jay_Feldman && git pull
nohup python3 scripts/dashboard-server.py --port 8750 >> ~/.hermes/desk.log 2>&1 &
curl -s localhost:8750/healthz      # expect {"ok": true, ...}
```

Add one hostname to the tunnel Bob already runs, keeping the 404 rule last:

```yaml
ingress:
  - hostname: hermes-hooks.nextwave.io
    service: http://127.0.0.1:8644
  - hostname: desk.nextwave.io
    service: http://127.0.0.1:8750
  - service: http_status:404
```

```bash
cloudflared tunnel route dns <tunnel-name> desk.nextwave.io
```

**Put Cloudflare Access on `desk.nextwave.io` before you open it the first time.**
`data.json` carries every interested lead's name, company and email. The server
refuses to bind anything but localhost for that reason; the tunnel is the only
thing exposing it, so the policy has to exist before the first page load.

---

## 6. Two cron entries on Bob — **you**, 5 minutes

Keep the desk current and the queue moving:

```cron
# refresh what the desk shows
*/15 * * * *  cd ~/LGJ/Jay_Feldman && BISON_API_KEY=… python3 scripts/build-dashboard-data.py >> ~/.hermes/desk-data.log 2>&1

# find new interested replies and stage drafts
7 * * * *     cd ~/LGJ/Jay_Feldman && BISON_API_KEY=… python3 scripts/fulfillment-sweep.py >> ~/.hermes/sweep.log 2>&1

# Monday digest: what to send, what to build, who needs a human
0 13 * * 1    cd ~/LGJ/Jay_Feldman && python3 scripts/weekly-list-demand.py >> ~/.hermes/demand.log 2>&1
```

Sending stays with Hermes, not cron: it reads
`scripts/dashboard-decisions.json`, and for each `approved` id not already in
`scripts/sent-log.json` runs `scripts/send-approved.py`. Every guard still runs
per send, including the live thread re-read.

---

## 7. Solve the gift links — **you**, one question

Every reply now offers a month of Consulti, and nothing can mint the links:
the documented API has no gift endpoint, and `POST /api/v1/gifts` returns
`403 Admin access required`.

Ask whoever owns Consulti billing, in this order:

1. **Is there a multi-use gift link?** If yes, paste it to me and the link goes
   in every reply instead of "say the word". One line changes.
2. **Can I have an admin-scoped API key?** Then a code mints per send and this
   stops being manual. This is the version that scales.
3. Failing both, generate links in the admin dashboard and paste them into the
   desk's pool. Thirty covers about three weeks at the current reply rate.

Until one of those, you send a link by hand when someone accepts.

---

## The weekly rhythm, once the above is done

| When | What | Who |
|---|---|---|
| Hourly | sweep finds new interested replies and stages drafts | Hermes |
| Every 15 min | desk data refreshed | Hermes |
| As they land | approve or skip on the desk | you, a few minutes |
| After each approval | guarded send, then desk refresh | Hermes |
| Monday | demand digest: send / build / needs-a-human | Hermes, you read it |
| When a list is missing | add a spec to `consulti-niche-filter-map.json`, run the builder | me, on request |

---

## Known open issues

- **The 500-versus-300 gap.** Three campaigns promise 500 contacts; fulfilment
  builds 300. Campaign 1145 also offers 50 local owners. Three leads have already
  caught it, one with the subject line "RE: 50 local owners". Either build 500 or
  change the live copy. Until then the reply agent is forbidden from stating any
  quantity.
- **The intent claim.** "companies needing creative support", "companies investing
  in SEO" and "companies planning a rebrand" are in the live copy and in
  `SIGNAL_TOPIC`. No Consulti filter expresses any of them. The agent is told to
  say so plainly; the copy probably should stop implying it.
- **30 burned threads.** Half the interested replies were answered with the wrong
  offer before we arrived. Recovering them needs different copy from the staged
  drafts, and the old agent off first.
- **Carl's niche is not servable.** Nonprofit Christian camps at $1M+ revenue:
  Consulti exposes neither revenue nor denomination. He gets 78 real camps and a
  reply that says so.
- **64 stale documents** in the artifact database, from the old dashboard's
  `queue` collection. Nothing reads them. Say the word and I will clear them.
