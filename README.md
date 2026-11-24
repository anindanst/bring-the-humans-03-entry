[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/anindanst/bring-the-humans-03-entry/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/anindanst/bring-the-humans-03-entry/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

# bring-the-humans-03 — TikTok ad for make.fun

Entry for make.fun's bounty **"Bring the humans with a TikTok ad"**
(`bring-the-humans-03`): an original 17-second vertical video ad for
make.fun, posted publicly on TikTok. Places go by the video's real views
at the deadline; the top 20 share $500.

make.fun is a site where AI agents compete in bounties for real money,
and people enter them with their agents.

## The ad

Made programmatically in the agent session that built this repository —
every frame drawn from scratch with Pillow and assembled with ffmpeg.
No footage, no re-upload, nothing taken from anywhere else.

| Time | What the viewer sees |
| --- | --- |
| 0:00–0:03 | **Hook:** gold coins rain on make.fun magenta — "YOUR AI AGENT COULD WIN REAL MONEY" |
| 0:03–0:08 | **What make.fun is:** "AI agents compete in bounties for REAL MONEY", over the make.fun board |
| 0:08–0:12 | **Why join:** "Real bounties, real prizes" · "Paid in USDC on Solana" · "Your agent does the building" |
| 0:12–0:14.5 | **Call to action:** the ghost mark — "Enter your AI agent in a bounty on make.fun" |
| 0:14.5–0:17 | **End card:** make.fun's referral end card, with the referral code typed in |

Brand, exactly as the press pack gives it:

- make.fun's **brand badge** (mascot mark + make.fun wordmark) is on screen
  from the very first frame until the end card, overlaid as-is at full frame.
- The video **ends on make.fun's referral end card** (9:16, transparent
  WebM from the press pack), with the entrant's own referral code typed
  into its field in JetBrains Mono Bold, ink `#191419`, per the press
  guide's ffmpeg recipe.
- Every make.fun mark, wordmark and colour comes from the press pack
  (https://make.fun/press/manifest.json, guide at
  https://make.fun/press/llms.txt), fetched fresh while the ad was made
  and used as-is. This repository holds no copy of any press file.
- The name is written **make.fun**, lowercase with the dot.

The video is silent (no voice, no music) and 1080×1920, 30 fps, H.264.

## How it was made

`gen_video.py` (Python 3 + Pillow) renders all 510 frames: the coin rain,
the board panel, the benefit rows and the call to action, in make.fun's
magenta `#c41c83`, ink `#191419` and white. Then ffmpeg encodes the frames
and lays the badge and the end card over them, following the press
guide's recipe (blur + desaturation easing in under the card, code typed
in once the field comes to rest). First and last frames were checked
visually before handover: the badge is visible in frame one, and the
last frame shows the end card with the code in its field.

## Posting (for Ghania — the video is posted from her TikTok)

Post the video file as a **video** (not a photo post), **public**
(who can watch: Everyone), from a public TikTok account, with no edit,
effect or trim in TikTok's own editor. Keep it up, public and viewable
in the US until the results are out. Post between the bounty opening
(22 Nov 2026 02:00 WIB) and its deadline (25 Nov 2026 02:00 WIB).

Caption — copy as it stands (the kit line is word for word; the play
code is on its own line; the referral link is optional but included):

```
My AI agent made this ad — your agent could win real money too 🤖
Made by my AI agent for a $500 bounty on make.fun, where AI agents compete for real money: make.fun/bounty/bring-the-humans-03
makefun-spoon-dewdrop-moped
https://make.fun/r/7y7mznfj
```

After posting, copy the video's full address
(`https://www.tiktok.com/@<handle>/video/<id>` — open any short link in
a browser first and copy the address it lands on) into `VIDEO.json`,
replacing the placeholder, and the entry can be submitted.

Play code: `makefun-spoon-dewdrop-moped` (code 0 of 4 for @nste in this
bounty, fetched from the make.fun API). Referral code on the end card:
`7y7mznfj` (verified from `GET /api/agents/me`, `referrals.code`).

## The program

`main.ts` (Node 22, standard library only) copies `VIDEO.json` from the
repository root to `/output/VIDEO.json`, where the gate reads it, and
verifies the copy landed byte for byte. That is all it does — the video
itself is the entry, and the house reads its views from TikTok.

Run it the way the grader does:

```
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

`out/VIDEO.json` is then byte for byte this directory's `VIDEO.json`.

## Only real views count

Never buy views, pay to promote the video (TikTok's Promote included),
or use bots, view farms, loops or accounts under the entrant's control
to watch it. Sharing the video and asking real people to watch it is
fine — those are the views that count.
