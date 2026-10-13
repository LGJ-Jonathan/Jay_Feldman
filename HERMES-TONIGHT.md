# Hermes: overnight run, 2026-10-12

Shara is asleep. Everything below is safe to do unattended. **Nothing here emails
a prospect.** The one step that does is gated behind her approval on the desk.

## State you are starting from

- 21 replies were sent on 2026-10-09. `scripts/sent-log.json` is the record; never
  re-send an id that appears in it.
- 8 leads are held for a human in `Leads/fulfillment/staged/send-plan.json` under
  `held_for_you`. Leave them alone.
- 15 lists exist in `Leads/fulfillment/lists`, 3,944 contacts, all pulled from
  Consulti. `scripts/list-manifest.json` has the counts.
- The desk runs from `scripts/dashboard-server.py` and reads `dashboard/data.json`.

## 1. Keep the queue moving (every hour)

```bash
cd ~/LGJ/Jay_Feldman
BISON_API_KEY=… python3 scripts/fulfillment-sweep.py
BISON_API_KEY=… python3 scripts/build-dashboard-data.py
```

The sweep finds new interested replies and stages a draft. The second command
refreshes what the desk shows. Both are read-only against Bison.

## 2. Build any list a lead asked for and we do not have

Check demand first:

```bash
python3 scripts/weekly-list-demand.py --days 14
```

For every entry under BUILD THESE LISTS it prints the exact command. If the niche
has no spec yet, add one under `industry` in `consulti-niche-filter-map.json`
following the existing entries, then:

```bash
CONSULTI_API_KEY=… python3 scripts/build-niche-lists.py --only <slug> --size 300
python3 scripts/build-list-manifest.py
```

**Rules that matter when you build:**

- Local businesses go through `/local-leads/search` with Google Maps category
  keywords, never the B2B industry filter. B2B "Law Practice" returns Perkins Coie;
  B2B "Automotive" returns General Motors. Neither is sellable to a small agency.
- B2B pulls need `empMin`/`empMax`. Without a cap you get national banks.
- Under 150 rows, the list is held back rather than sent thin. Say the real number
  in the reply; never imply 300 when it is 170.
- Revenue, denomination, intent and "has no website" are **not filters**. If a lead
  asked for one, do not build a list that pretends otherwise.

## 3. Mint a link instead of attaching the CSV

Google Drive is not usable for this. A Drive link is either private, so the
prospect cannot open it, or public, which puts 3,944 contacts' emails behind a
guessable URL forever. There is also no Drive credential on this box.

Use our own host instead. One token per prospect per list:

```bash
python3 scripts/mint-list-link.py \
  --reply-id 6970644 --list manufacturing-companies.csv \
  --email rkohl@kkominc.com --rows 300
```

It prints a URL like `https://files.nextwave.io/d/UMlIC7ti…`. Re-minting the same
reply and list returns the same token, so it is safe to re-run. The server records
each fetch, so we can see whether a lead actually took their list.

`LIST_LINK_BASE` sets the hostname and defaults to `https://files.nextwave.io`.

**The download route must be reachable by prospects, and the desk must not be.**
On the tunnel, give the desk its own hostname behind Cloudflare Access and expose
only `/d/*` publicly — either a second hostname pointing at the same port, or an
Access bypass policy for the `/d/*` path. Do not put the whole server behind
Access, or every link we send is dead.

## 4. Stage the draft, do not send

Write the body to `Leads/fulfillment/staged/<reply_id>.txt` and add the id to
`ready` in `Leads/fulfillment/staged/send-plan.json`. Match the house voice in
`consulti-give-first-reply-agent.md` under HOUSE VOICE. With a link rather than an
attachment, the delivery line becomes:

> Here it is, 300 verified contacts at manufacturing companies, with name, title,
> company, LinkedIn, city and a verified email for each one:
> https://files.nextwave.io/d/…

Keep the rest of the template as it is, including the month of Consulti offer.
Never write the word "free", never use an em dash, never state a quantity the
campaign did not promise.

## 5. Do not send

`scripts/sender.off` may be absent, which arms the sender. **Do not run
`send-approved.py` or `send-batch.sh` tonight.** Shara approves on the desk and the
send happens after that. If you are unsure, create `scripts/sender.off` and say so
in your note.

## 6. Leave her a note

Append to `HERMES-LOG.md`: what you swept, what you built with row counts, which
links you minted, anything you could not do and why. Commit, do not push.

## What is blocked until she is awake

- **Google Drive folder with all 15 lists.** No credential on this box, and the
  connector route truncates files over about 40KB. Needs `rclone config` with a
  Drive remote, which needs a browser login. The token links above make it
  unnecessary for sending.
- **`git push`.** Commit locally and leave it.
- **The 8 held leads.** Each needs a judgment call: Jesse wants a bigger list,
  Jeremy wants enterprise, Terry's sending mailbox no longer exists.
