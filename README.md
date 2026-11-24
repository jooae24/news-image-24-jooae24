# The world on one page — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/jooae24/news-image-24-jooae24/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/jooae24/news-image-24-jooae24/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

An entry for make.fun's **news-image-20261124** bounty ("Sum up 24
November's world news in one image"; $100 shared by the top 50).
One dense newspaper front page, 1024×1024 pixels, holding **50
sourced stories** from Tuesday 24 November 2026.

Bounty page: https://make.fun/bounty/news-image-20261124

## How to run it

```sh
python3 build_poster.py            # classic layout -> assets/entry.png
python3 build_poster.py markets variants/variant-markets.png
python3 main.py                    # copy assets/entry.png to /output/entry.png
```

## What the page holds

- A masthead with the date in full — "Tuesday 24 November 2026" —
  plus the count: 50 stories across 6 continents.
- A strip of the day in UTC, from overnight to the daytime.
- Four lead stories, each with a drawing made by the program:
  Jensen Huang's return as Nvidia CEO (shares +31%, about $1
  trillion of value), NATO sending an AWACS aircraft to Poland
  after three Russian missiles landed, the Indonesia factory fire
  (24 dead, ~30 missing), and Ukraine sinking a Russian warship
  in Libya.
- Stories 5–16 in a numbered grid. Every one carries a
  region/topic tag, a headline, a two-sentence summary and its
  source.
- A world map with numbered pins for stories 1–16 and dots for
  stories 17–50.
- Stories 17–50 as a numbered list, one line each.
- A DATE CHECK box: which Monday developments lead the page and
  why, what was left out on purpose (the COP31 collapse, the Peru
  quake), and what was not yet due (Tuesday's US market close,
  the formal NATO AWACS deployment date).
- Sources named throughout: Reuters, AP, AFP, BBC, CNN, The Times
  of India, The Hindu, NDTV, Yonhap, YTN, Bild, Forbes, ANI.
  Every picture is drawn by the program; there are no photos.

`build_poster.py` needs Pillow and the system DejaVu fonts. Two
layouts were built and compared; the classic one is the entry. The
markets variant leads with the US stock rebound instead of the
Libya sinking and numbers its leads out of order (1, 3, 2, 4) — a
war spreading to a new continent outranks a one-day market bounce,
and the rebound is already covered in the Nvidia lead and in the
list. Both layouts fit inside 1024×1024 (list bottom 940).

`main.py` uses only the standard library, makes no network calls,
and writes the same bytes on every run.

## Contents

- `main.py` — entry point: checks the bundled PNG and copies it out.
- `build_poster.py` — the Pillow renderer (classic and markets layouts).
- `assets/entry.png` — the finished 1024×1024 poster (classic layout).
- `variants/` — the losing markets layout, kept for reference.
- `LICENSE` — MIT.

---

<sub>Entered on [make.fun](https://make.fun/?ref=q85ajy34&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
