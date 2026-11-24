#!/usr/bin/env python3
"""Tuesday 24 November 2026 front page — one 1024x1024 newspaper poster.

Renders a dense broadsheet-style front page: a black masthead, a UTC
timeline strip, four lead stories with hand-drawn illustrations, a
twelve-story grid, a pinned world map, a numbered list of the remaining
stories, and a DATE CHECK footer that is honest about which items
happened on Monday but were first reported on Tuesday morning in Asia.

Two editorial variants:
    classic  — leads: Nvidia return, NATO AWACS, Indonesia fire, Libya
    markets  — leads: Nvidia return, Indonesia fire, NATO AWACS, US
               stocks rebound; Libya warship moves into the grid and
               the chess championship moves to the top of the list.

Usage:
    python3 build_poster.py classic assets/entry.png
    python3 build_poster.py markets variants/variant-markets.png

Only the standard library and Pillow are used. No network access.
The same command always writes byte-identical PNGs.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (248, 243, 232)      # warm newsprint
INK = (18, 18, 18)
GREY = (90, 90, 86)
RED = (178, 34, 28)
NAVY = (28, 52, 96)
GOLD = (212, 175, 55)
SEA = (198, 222, 235)        # map ocean
LAND = (196, 214, 166)       # map land
LAND_LINE = (120, 140, 100)
CARD = (255, 253, 247)
CARD_LINE = (178, 168, 148)
SKY = (208, 228, 240)
GREEN = (28, 120, 60)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

_FONT_CACHE = {}


def font(sans=True, size=12, bold=False):
    """Load a DejaVu font, cached by (family, size, bold)."""
    key = (sans, size, bold)
    if key not in _FONT_CACHE:
        if sans:
            name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        else:
            name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
        _FONT_CACHE[key] = ImageFont.truetype(FONT_DIR + "/" + name, size)
    return _FONT_CACHE[key]


def text_w(draw, text, fnt):
    """Pixel width of text in a font."""
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if text_w(draw, trial, fnt) <= max_w:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_lines(draw, x, y, lines, fnt, lh, fill, max_lines=None,
               max_w=None):
    """Draw wrapped lines; truncate with an ellipsis past max_lines."""
    shown = lines
    if max_lines is not None and len(lines) > max_lines:
        shown = list(lines[:max_lines])
        last = shown[-1]
        if max_w is not None:
            while last and draw.textlength(last + "…", font=fnt) > max_w:
                last = last[:-1]
            shown[-1] = last + "…"
    for i, line in enumerate(shown):
        draw.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(shown) * lh


def block(draw, x, y, text, fnt, max_w, lh, fill, max_lines=None):
    """Wrap text and draw it; returns the y just below the block."""
    return draw_lines(draw, x, y, wrap(draw, text, fnt, max_w),
                      fnt, lh, fill, max_lines=max_lines, max_w=max_w)


def rule(draw, x0, y, x1, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)

# --- story data ----------------------------------------------------------
# Leads: number, kicker, dateline, headline, summary, source, art key.
LEADS_CLASSIC = [
    {
        "n": 1, "kicker": "TECH · MARKETS", "place": "SANTA CLARA · NVIDIA",
        "art": "nvidia",
        "headline": "Huang is back: Nvidia reinstates CEO, shares jump 31%",
        "summary": "Nvidia's board unanimously reinstated co-founder "
                   "Jensen Huang as CEO, under pressure from Trump, who "
                   "said he convinced the board. Shares jumped 31–33%, "
                   "adding about $1 trillion in value.",
        "source": "Source: Reuters, Times of India, NDTV",
    },
    {
        "n": 2, "kicker": "EUROPE · NATO", "place": "WARSAW · POLAND",
        "art": "nato",
        "headline": "NATO sends AWACS to Poland after missiles land",
        "summary": "NATO will deploy an AWACS early-warning aircraft to "
                   "Poland after three Russian Kh-101 cruise missiles "
                   "landed in the country on Friday. Allies held Russia "
                   "'fully responsible'.",
        "source": "Source: Reuters",
    },
    {
        "n": 3, "kicker": "ASIA · INDONESIA", "place": "CIKANDE · BANTEN",
        "art": "factory",
        "headline": "Indonesia factory fire: 24 dead, ~30 missing",
        "summary": "Indonesia confirmed 24 people killed in a fire at "
                   "the PT Fonusa Agung Mulia candy factory in Cikande; "
                   "rescuers searched unstable wreckage for about 30 "
                   "people still missing.",
        "source": "Source: Reuters, AP, Al Jazeera",
    },
    {
        "n": 4, "kicker": "AFRICA · LIBYA", "place": "BENGHAZI · LIBYA",
        "art": "warship",
        "headline": "Ukraine sinks Russian warship in Libya",
        "summary": "Ukraine sank the Russian naval corvette Merkury in "
                   "the Libyan port of Benghazi using maritime drones "
                   "on Sunday, President Zelenskiy said. The UN warned "
                   "Libya must not become a battleground.",
        "source": "Source: Reuters, AFP",
    },
]

LEADS_MARKETS = [
    LEADS_CLASSIC[0],
    LEADS_CLASSIC[2],
    LEADS_CLASSIC[1],
    {
        "n": 4, "kicker": "MARKETS · USA", "place": "NEW YORK · WALL ST",
        "art": "markets",
        "headline": "US stocks rebound: S&P +4.7%, Nasdaq +6.5%",
        "summary": "US stocks rebounded sharply on Monday as Nvidia's "
                   "return lifted tech: the S&P 500 rose 4.73% to "
                   "7,237 and the Nasdaq 6.51% to 24,090, ending a "
                   "seven-day losing streak.",
        "source": "Source: Reuters, Global Eye 24",
    },
]

# Grid stories 5–16: (kicker, headline, summary, source).
GRID_CLASSIC = [
    ("ASIA · SOUTH KOREA",
     "Russian aircraft enters airspace; Ulleung warning",
     "South Korea briefly issued an evacuation warning for Ulleung "
     "island after a Russian aircraft entered its airspace.",
     "Reuters, YTN"),
    ("GLOBAL · CLIMATE",
     "COP31 flop triggers backlash in Australia",
     "Blame for the collapse of the UN climate talks in Antalya began "
     "on Monday; Pacific nations expressed despair.", "Reuters"),
    ("MIDDLE EAST · IRAN",
     "\u201cWe will use all our tools\u201d vs US blockade",
     "Iran will use all its tools to confront the US naval blockade, "
     "the foreign ministry spokesperson said.", "Reuters"),
    ("AMERICAS · USA",
     "US sanctions dozens over Iran shadow banking",
     "The US imposed sanctions on dozens of people and entities linked "
     "to Iran's shadow banking networks.", "Reuters"),
    ("MIDDLE EAST · GAZA",
     "Israeli strikes kill 3, incl. UN worker",
     "Israeli airstrikes killed at least three people in Gaza on "
     "Monday, including a UN Palestinian agency worker.", "Reuters"),
    ("AMERICAS · USA",
     "Trump halts Iowa lead azide detonation",
     "Trump said he ordered the US Army to pause detonation of a "
     "deteriorating stockpile of toxic lead azide in Iowa.", "Reuters"),
    ("MIDDLE EAST · IRAN",
     "Singer flogged: 74 lashes each",
     "An Iranian singer and four members of her production team each "
     "received 74 lashes after being sentenced.", "Reuters"),
    ("EUROPE · GERMANY",
     "Berlin to use Kyiv's Delta battle tool",
     "Germany and Ukraine signed a letter of intent to let the "
     "Bundeswehr use Kyiv's Delta battle management system.",
     "Reuters"),
    ("EUROPE · RUSSIA",
     "Murmansk governor detained",
     "The governor of Russia's Murmansk region was detained on "
     "suspicion of embezzlement, authorities said.", "Reuters"),
    ("SPORT · TENNIS",
     "Alcaraz wins maiden ATP Finals title",
     "Carlos Alcaraz won his first ATP Finals title, beating Alexander "
     "Zverev in the final in Turin.", "Times of India, Reuters"),
    ("SPORT · CRICKET",
     "India–NZ first Test ends in a draw",
     "India and New Zealand played out a draw in the first Test at "
     "Basin Reserve, Wellington, after a visitors' fightback.",
     "Times of India"),
    ("SPORT · CHESS",
     "Gukesh defends world title in Geneva",
     "India's D Gukesh begins his World Chess Championship title "
     "defence against Uzbekistan's Javokhir Sindarov.", "Times of India"),
]

GRID_MARKETS = [
    ("AFRICA · LIBYA",
     "Ukraine sinks Russian warship in Libya",
     "Ukraine sank the Russian corvette Merkury in Benghazi using "
     "maritime drones on Sunday, President Zelenskiy said.", "Reuters"),
    GRID_CLASSIC[0], GRID_CLASSIC[1], GRID_CLASSIC[2],
    GRID_CLASSIC[3], GRID_CLASSIC[4], GRID_CLASSIC[5],
    GRID_CLASSIC[6], GRID_CLASSIC[7], GRID_CLASSIC[8],
    GRID_CLASSIC[9], GRID_CLASSIC[10],
]

# Timeline: (time label, text).
TIMELINE = [
    ("OVERNIGHT", "Nvidia board reinstates Jensen Huang as CEO; shares "
                  "jump 31% at the open."),
    ("~00:30 UTC", "South Korea issues an evacuation warning for "
                    "Ulleung island."),
    ("02:05 UTC", "Indonesia confirms 24 dead in the factory fire; "
                   "about 30 still missing."),
    ("06:00 UTC", "Trump hails Huang's return: the board made \u201cthe "
                  "correct and proper decision\u201d."),
    ("DAY", "NATO to send an AWACS aircraft to Poland after the missile "
            "incident."),
    ("DAY", "Gukesh–Sindarov World Chess Championship begins in Geneva."),
]

# List stories 17–50: (number, one-line text, lon, lat).
LIST_CLASSIC = [
    (17, "Russian drone briefly violates Polish airspace; Poland held "
         "fire after it changed course.", 19, 50),
    (18, "UK sanctions top Myanmar military leaders after Rohingya "
         "genocide ruling.", 96, 20),
    (19, "UN warns Libya should not turn into a battleground for the war "
         "in Ukraine.", 13, 32),
    (20, "Ukraine drones hit an oil processing plant deep inside Russia, "
         "1,200 km away.", 44, 54),
    (21, "Germany sends tanks for Lithuania by rail, not through Poland, "
         "to avoid provoking Putin.", 24, 55),
    (22, "UN chief urges an AI safety framework to be created next year.",
     -74, 40),
    (23, "US stocks rebound sharply as Nvidia jumps; S&P 500 +4.7%, "
         "Nasdaq +6.5%.", -73, 41),
    (24, "Democrats propose a 10-year limit to protect immigrants from "
         "Trump's deportation crackdown.", -79, 38),
    (25, "Federal appeals court gives Trump a path to erasing his hush "
         "money conviction.", -76, 42),
    (26, "FIFA Congress selects hosts for the 2031 and 2035 Women's "
         "World Cups.", 8, 47),
    (27, "Denmark's top court backs the hardline immigration "
         "\u201cghetto law\u201d.", 12, 55),
    (28, "Bangladesh vows to arrest ex-PM Sheikh Hasina if she returns "
         "from India.", 90, 23),
    (29, "China sets 2030 targets to strengthen elderly care and "
         "childcare support.", 116, 40),
    (30, "South Korea's president nominates a new foreign minister and "
         "intelligence chief.", 126, 36),
    (31, "Armenia proposes a new constitution to advance peace talks "
         "with Azerbaijan.", 44, 40),
    (32, "Sensex falls 1,484 points (1.77%) to 82,435; Nifty drops 451.",
     72, 19),
    (33, "India and China hold military-level talks in Arunachal Pradesh "
         "to reduce border tensions.", 94, 28),
    (34, "PM Modi inaugurates an AI centre at IIT Patna, launches a "
         "Rs 400 crore research park.", 85, 25),
    (35, "Supreme Court grants bail to a Godhra train burning convict on "
         "medical grounds.", 76, 29),
    (36, "Chief Justice of India calls for mandatory legal aid work and "
         "AI guidelines in law courses.", 78, 27),
    (37, "A supermoon is about to meet the Pleiades, the \u2018Seven "
         "Sisters\u2019, in the night sky.", 0, 51),
    (38, "Chicago's O'Hare issues a brief ground stop over a staffing "
         "shortage amid the Thanksgiving rush.", -87, 41),
    (39, "Lahore tops the global pollution ranking again as AQI crosses "
         "500.", 74, 31),
    (40, "A 4.0-magnitude earthquake strikes Pakistan near the "
         "Afghanistan border.", 70, 34),
    (41, "King Charles reached out to Meghan Markle after her father "
         "Thomas Markle's arrest over child abuse images.", -2, 52),
    (42, "Dutch transgender activist Jason Bhugwandass dies by "
         "euthanasia at 28.", 5, 52),
    (43, "Around 450 schools in Germany receive bomb threats via email.",
     11, 51),
    (44, "Chinese official sentenced to death for leaking 100 "
         "intelligence reports, including 35 state secrets.", 114, 38),
    (45, "Mossad saved Taylor Swift's Vienna concerts from an "
         "ISIS-inspired terror plot, its former chief reveals.", 16, 48),
    (46, "Kash Patel's $41 million fraud probe: child centres raided in "
         "Minnesota.", -93, 45),
    (47, "Trump targets Newsom in a DOJ speech over commuting 548 death "
         "sentences.", -75, 40),
    (48, "A former mayor of Mississippi's capital is sentenced to 37 "
         "months in prison in a bribery scheme.", -90, 32),
    (49, "Greece and Israel negotiate significant military deals worth "
         "around \u20ac1 billion.", 23, 38),
    (50, "Russia is said to have tried to assassinate a Ukrainian artist "
         "in Poland and Denmark.", 23, 54),
]

# Markets variant: chess moves to the top of the list, the weakest-sourced
# item (50) drops out so the list still runs 17–50.
LIST_MARKETS = [
    (17, "Gukesh defends his world chess title vs Sindarov in Geneva; "
         "the championship begins today.", 6, 46),
] + [(n + 1, t, lo, la) for (n, t, lo, la) in LIST_CLASSIC[:33]]

DATE_CHECK = (
    "× Huang's return was announced on Monday evening in the US and "
    "first reported across Asia on Tuesday morning; it leads the page "
    "because Tuesday's papers worldwide lead with it. The Ukraine–Libya "
    "sinking happened on Sunday; Zelenskiy confirmed it on Monday and "
    "it was reported on Tuesday. The Indonesia fire broke out on "
    "Saturday; the confirmed toll of 24 came on Monday and was reported "
    "on Tuesday morning. LEFT OUT ON PURPOSE: the COP31 collapse "
    "(Sunday 22 Nov) appears only as a follow-up; the magnitude 6.9 "
    "Peru earthquake (Friday 20 Nov) predates Tuesday. NOT YET: "
    "Tuesday's US market close and the formal NATO AWACS deployment "
    "date are due after this page was drawn."
)

SOURCES = ("Sources: Reuters, AP, AFP, BBC, CNN, The Times of India, "
           "The Hindu, NDTV, Yonhap, YTN, Bild, Forbes, ANI. "
           "Every picture is drawn by the program; there are no photos.")

# Map pins for stories 1–16: (lon, lat). Offsets keep neighbours apart.
PINS_CLASSIC = {
    1: (-122, 37), 2: (21, 52), 3: (106, -6), 4: (20, 32),
    5: (131, 37), 6: (149, -35), 7: (51, 35), 8: (-77, 39),
    9: (34, 31), 10: (-93, 42), 11: (60, 27), 12: (15, 54),
    13: (33, 69), 14: (7, 45), 15: (175, -41), 16: (6, 46),
}

PINS_MARKETS = {
    1: (-122, 37), 2: (106, -6), 3: (21, 52), 4: (-74, 40),
    5: (20, 32), 6: (131, 37), 7: (149, -35), 8: (51, 35),
    9: (-77, 39), 10: (34, 31), 11: (-93, 42), 12: (60, 27),
    13: (15, 54), 14: (33, 69), 15: (7, 45), 16: (175, -41),
}

VARIANTS = {
    "classic": (LEADS_CLASSIC, GRID_CLASSIC, LIST_CLASSIC, PINS_CLASSIC),
    "markets": (LEADS_MARKETS, GRID_MARKETS, LIST_MARKETS, PINS_MARKETS),
}

# Simplified continent outlines (lon, lat), drawn as a stylised strip map.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
     (-100, 73), (-90, 74), (-85, 70), (-80, 73), (-76, 62),
     (-70, 58), (-65, 60), (-60, 55), (-55, 52), (-60, 47),
     (-65, 44), (-70, 42), (-75, 38), (-76, 35), (-80, 32),
     (-81, 26), (-84, 30), (-88, 29), (-91, 19), (-95, 18),
     (-97, 16), (-92, 15), (-87, 13), (-83, 10), (-79, 9),
     (-85, 11), (-90, 14), (-95, 16), (-100, 18), (-105, 20),
     (-110, 23), (-114, 29), (-120, 34), (-124, 40), (-124, 48),
     (-130, 55), (-140, 60), (-150, 61), (-158, 58), (-165, 60)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-80, -12),
     (-77, -18), (-73, -24), (-70, -30), (-70, -37), (-71, -44),
     (-69, -50), (-66, -55), (-68, -52), (-65, -45), (-62, -40),
     (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
     (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
     (-54, 2), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
     (-76, 10)],
    # Europe (coarse)
    [(-10, 36), (-9, 43), (-2, 48), (-4, 52), (-8, 54), (-5, 58),
     (0, 58), (5, 58), (8, 57), (12, 55), (18, 56), (21, 55),
     (24, 58), (28, 60), (30, 62), (30, 70), (25, 71), (20, 70),
     (18, 69), (15, 68), (12, 66), (10, 64), (5, 60), (5, 58),
     (8, 55), (10, 54), (8, 53), (5, 53), (0, 51), (-2, 50),
     (-5, 49), (-1, 46), (-4, 44), (-2, 43), (-6, 44), (-9, 43),
     (-10, 38)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 25), (-10, 30), (-5, 33), (0, 36),
     (10, 37), (15, 36), (20, 32), (25, 32), (30, 31), (32, 29),
     (34, 27), (36, 23), (38, 18), (40, 15), (43, 11), (48, 11),
     (51, 10), (50, 5), (48, 0), (44, -5), (40, -10), (38, -18),
     (35, -24), (32, -29), (28, -33), (22, -35), (18, -33), (15, -28),
     (13, -20), (12, -15), (13, -10), (12, -5), (9, 0), (8, 4),
     (4, 6), (-2, 5), (-8, 5), (-13, 8), (-17, 12)],
    # Asia
    [(30, 36), (35, 36), (40, 38), (44, 39), (48, 40), (50, 42),
     (53, 44), (55, 46), (58, 48), (60, 50), (62, 52), (65, 55),
     (68, 58), (70, 62), (72, 66), (75, 70), (78, 72), (82, 73),
     (86, 74), (90, 75), (95, 76), (100, 77), (105, 77), (110, 76),
     (115, 74), (120, 73), (125, 72), (130, 71), (135, 71), (140, 72),
     (145, 72), (150, 70), (155, 69), (158, 66), (160, 62), (162, 60),
     (160, 56), (158, 52), (155, 50), (150, 48), (145, 44), (142, 42),
     (140, 38), (138, 35), (135, 34), (132, 33), (130, 31), (127, 34),
     (126, 38), (122, 38), (120, 32), (118, 28), (115, 24), (112, 21),
     (110, 20), (108, 16), (106, 10), (104, 9), (101, 7), (99, 10),
     (97, 14), (94, 17), (92, 21), (90, 22), (88, 22), (86, 20),
     (84, 18), (81, 15), (79, 13), (77, 8), (76, 10), (74, 15),
     (72, 20), (70, 21), (68, 23), (66, 25), (64, 25), (62, 25),
     (60, 25), (58, 26), (56, 26), (54, 27), (52, 28), (50, 29),
     (48, 30), (46, 29), (44, 29), (42, 30), (40, 31), (38, 33),
     (36, 36), (34, 36), (32, 36)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (115, -35), (118, -35),
     (122, -34), (126, -32), (129, -32), (132, -32), (135, -35),
     (138, -35), (140, -38), (143, -39), (146, -39), (149, -37),
     (150, -37), (153, -32), (153, -27), (151, -24), (149, -20),
     (146, -19), (143, -17), (142, -15), (142, -11), (140, -12),
     (137, -12), (136, -15), (134, -12), (132, -11), (130, -13),
     (128, -14), (126, -14), (124, -15), (122, -17), (120, -19),
     (117, -20), (114, -21)],
]


# --- lead illustrations --------------------------------------------------
def art_nvidia(d, x0, y0, x1, y1):
    """A green chip with a rising chart and the +31% tag."""
    d.rectangle([x0, y0, x1, y1], fill=(16, 40, 24))
    # chip
    cx0, cy0, cx1, cy1 = x0 + 8, y0 + 8, x0 + 62, y0 + 44
    d.rectangle([cx0, cy0, cx1, cy1], fill=(28, 120, 60),
                outline=(120, 200, 140))
    for px in (cx0 + 12, cx0 + 26, cx0 + 40):
        d.line([(px, cy0 - 5), (px, cy0)], fill=(120, 200, 140), width=2)
        d.line([(px, cy1), (px, cy1 + 5)], fill=(120, 200, 140), width=2)
    d.text((cx0 + 6, cy0 + 10), "NVDA", font=font(True, 13, True),
           fill=(255, 255, 255))
    # rising line
    pts = [(x0 + 70, y0 + 44), (x0 + 92, y0 + 36), (x0 + 112, y0 + 40),
           (x0 + 134, y0 + 26), (x0 + 156, y0 + 30), (x0 + 178, y0 + 12),
           (x0 + 198, y0 + 16)]
    d.line(pts, fill=(120, 230, 140), width=3)
    d.polygon([(x0 + 198, y0 + 16), (x0 + 188, y0 + 14),
               (x0 + 196, y0 + 24)], fill=(120, 230, 140))
    d.text((x1 - 62, y0 + 6), "+31%", font=font(True, 20, True),
           fill=(120, 230, 140))
    d.text((x0 + 6, y1 - 12), "board vote unanimous · Trump pushed",
           font=font(True, 9), fill=(200, 220, 205))


def art_nato(d, x0, y0, x1, y1):
    """An AWACS plane under radar sweeps over a dark sky."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.arc([x0 + 120, y0 - 60, x0 + 220, y0 + 40], 20, 160,
          fill=NAVY, width=2)
    d.arc([x0 + 130, y0 - 50, x0 + 210, y0 + 30], 20, 160,
          fill=(90, 120, 170), width=1)
    # fuselage + radar dome
    d.ellipse([x0 + 60, y0 + 14, x0 + 170, y0 + 34], fill=NAVY)
    d.ellipse([x0 + 100, y0 + 6, x0 + 140, y0 + 18], fill=(60, 80, 120))
    d.polygon([(x0 + 170, y0 + 20), (x0 + 196, y0 + 24),
               (x0 + 170, y0 + 28)], fill=NAVY)
    d.polygon([(x0 + 70, y0 + 30), (x0 + 90, y0 + 44),
               (x0 + 96, y0 + 30)], fill=NAVY)
    d.polygon([(x0 + 130, y0 + 30), (x0 + 150, y0 + 44),
               (x0 + 156, y0 + 30)], fill=NAVY)
    d.text((x0 + 6, y0 + 2), "AWACS", font=font(True, 13, True),
           fill=NAVY)
    d.text((x0 + 6, y1 - 12), "3 Russian missiles landed Friday",
           font=font(True, 9), fill=GREY)


def art_factory(d, x0, y0, x1, y1):
    """A factory block with flames and smoke, and the death toll."""
    d.rectangle([x0, y0, x1, y1], fill=(52, 44, 40))
    d.rectangle([x0 + 14, y0 + 26, x0 + 120, y0 + 52], fill=(120, 110, 100))
    d.rectangle([x0 + 120, y0 + 18, x0 + 132, y0 + 52], fill=(90, 82, 74))
    d.rectangle([x0 + 138, y0 + 34, x0 + 190, y0 + 52],
                fill=(120, 110, 100))
    # flames
    for fx, fh in ((x0 + 30, 18), (x0 + 60, 24), (x0 + 92, 16),
                   (x0 + 150, 14)):
        d.polygon([(fx - 8, y0 + 28), (fx, y0 + 28 - fh),
                   (fx + 8, y0 + 28)], fill=(232, 120, 30))
        d.polygon([(fx - 4, y0 + 28), (fx, y0 + 28 - fh + 8),
                   (fx + 4, y0 + 28)], fill=(240, 200, 60))
    d.ellipse([x0 + 150, y0 + 2, x0 + 172, y0 + 16], fill=(150, 150, 150))
    d.ellipse([x0 + 170, y0 - 2, x0 + 192, y0 + 12], fill=(170, 170, 170))
    d.text((x1 - 66, y0 + 4), "24 DEAD", font=font(True, 15, True),
           fill=(255, 210, 90))
    d.text((x0 + 6, y1 - 12), "~30 still missing in the wreckage",
           font=font(True, 9), fill=(220, 215, 205))


def art_warship(d, x0, y0, x1, y1):
    """A grey corvette on a dark sea, hit by a drone strike."""
    d.rectangle([x0, y0, x1, y1], fill=(24, 48, 84))
    d.ellipse([x1 - 34, y0 + 6, x1 - 12, y0 + 28], fill=(232, 200, 120))
    # hull
    d.polygon([(x0 + 20, y0 + 34), (x0 + 170, y0 + 34),
               (x0 + 185, y0 + 44), (x0 + 30, y0 + 44)], fill=(150, 160, 170))
    d.rectangle([x0 + 60, y0 + 24, x0 + 110, y0 + 34], fill=(120, 130, 140))
    d.line([(x0 + 85, y0 + 24), (x0 + 85, y0 + 14)], fill=(200, 200, 200),
           width=2)
    # explosion + drone
    d.polygon([(x0 + 150, y0 + 20), (x0 + 160, y0 + 30),
               (x0 + 172, y0 + 22), (x0 + 180, y0 + 32),
               (x0 + 164, y0 + 36), (x0 + 158, y0 + 44),
               (x0 + 146, y0 + 34)], fill=(240, 160, 40))
    d.ellipse([x0 + 34, y0 + 8, x0 + 46, y0 + 16], fill=(220, 220, 220))
    for wx in range(x0 + 10, x1 - 8, 22):
        d.line([(wx, y0 + 50), (wx + 12, y0 + 50)], fill=(120, 170, 210),
               width=2)
    d.text((x0 + 6, y1 - 12), "Merkury hit in Benghazi harbour",
           font=font(True, 9), fill=(220, 225, 235))


def art_markets(d, x0, y0, x1, y1):
    """A green market board: S&P and Nasdaq up, Dow up."""
    d.rectangle([x0, y0, x1, y1], fill=(18, 46, 30))
    pts = [(x0 + 8, y0 + 44), (x0 + 40, y0 + 38), (x0 + 70, y0 + 42),
           (x0 + 100, y0 + 30), (x0 + 130, y0 + 34), (x0 + 160, y0 + 18),
           (x0 + 190, y0 + 22), (x0 + 210, y0 + 8)]
    d.line(pts, fill=(120, 230, 140), width=3)
    d.polygon([(x0 + 210, y0 + 8), (x0 + 200, y0 + 6),
               (x0 + 208, y0 + 16)], fill=(120, 230, 140))
    d.text((x0 + 8, y0 + 6), "S&P +4.7%", font=font(True, 14, True),
           fill=(255, 255, 255))
    d.text((x0 + 100, y0 + 6), "NASDAQ +6.5%", font=font(True, 14, True),
           fill=(120, 230, 140))
    d.text((x0 + 6, y1 - 12), "best day since April 2025 · Dow +1,448",
           font=font(True, 9), fill=(200, 220, 205))


ARTS = {"nvidia": art_nvidia, "nato": art_nato, "factory": art_factory,
        "warship": art_warship, "markets": art_markets}

# --- sections ------------------------------------------------------------
def draw_masthead(d):
    d.rectangle([0, 0, W, 94], fill=(12, 12, 12))
    d.text((14, 8), "THE WORLD IN ONE PAGE",
           font=font(True, 33, True), fill=(255, 255, 255))
    d.text((14, 50), "Tuesday 24 November 2026",
           font=font(False, 29, True), fill=GOLD)
    d.text((640, 10), "50 STORIES · 6 CONTINENTS",
           font=font(True, 15, True), fill=(255, 255, 255))
    d.text((640, 34), "TUESDAY EDITION · ALL TIMES UTC",
           font=font(True, 11), fill=(190, 190, 185))
    d.text((640, 52), "Every story happened or was first",
           font=font(True, 10), fill=(170, 170, 165))
    d.text((640, 66), "reported on Tuesday 24 Nov 2026*",
           font=font(True, 10), fill=(170, 170, 165))


def draw_timeline(d):
    y = 100
    d.text((10, y), "THE DAY IN UTC", font=font(True, 12, True), fill=RED)
    rule(d, 10, y + 16, W - 10, width=2, fill=RED)
    col_w = (W - 20) // 6
    for i, (when, text) in enumerate(TIMELINE):
        x = 10 + i * col_w
        d.text((x, y + 20), when, font=font(True, 11, True), fill=RED)
        block(d, x, y + 32, text, font(True, 9), col_w - 8, 11, INK,
              max_lines=2)


def draw_lead(d, story, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE)
    d.rectangle([x, y, x + 22, y + 22], fill=RED)
    d.text((x + 6, y + 3), str(story["n"]), font=font(True, 13, True),
           fill=(255, 255, 255))
    d.text((x + 28, y + 4), story["kicker"], font=font(True, 10, True),
           fill=RED)
    ARTS[story["art"]](d, x + 6, y + 28, x + w - 6, y + 88)
    d.text((x + 6, y + 92), story["place"], font=font(True, 9, True),
           fill=NAVY)
    block(d, x + 6, y + 106, story["headline"], font(False, 13, True),
          w - 12, 15, INK, max_lines=3)
    block(d, x + 6, y + 152, story["summary"], font(True, 9),
          w - 12, 11, INK, max_lines=4)
    d.text((x + 6, y + h - 13), story["source"], font=font(True, 8),
           fill=GREY)


def draw_leads(d, leads):
    y, h = 156, 208
    cw = (W - 20 - 3 * 8) // 4
    for i, story in enumerate(leads):
        draw_lead(d, story, 10 + i * (cw + 8), y, cw, h)


def draw_grid_card(d, num, kicker, headline, summary, source, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE)
    d.text((x + 6, y + 4), str(num), font=font(True, 11, True), fill=RED)
    d.text((x + 24, y + 5), kicker, font=font(True, 9, True), fill=RED)
    block(d, x + 6, y + 19, headline, font(False, 11, True), w - 12, 13,
          INK, max_lines=2)
    block(d, x + 6, y + 46, summary, font(True, 9), w - 12, 11, INK,
          max_lines=2)
    d.text((x + 6, y + h - 11), "Source: " + source,
           font=font(True, 8), fill=GREY)


def draw_grid(d, grid):
    y = 366
    d.text((10, y), "THE DAY'S NEWS · 5–16", font=font(True, 12, True),
           fill=RED)
    rule(d, 10, y + 16, W - 10, width=2, fill=RED)
    cw = (W - 20 - 3 * 8) // 4
    ch, gap = 76, 4
    for i, (kicker, headline, summary, source) in enumerate(grid):
        row, col = divmod(i, 4)
        x = 10 + col * (cw + 8)
        yy = 386 + row * (ch + gap)
        draw_grid_card(d, 5 + i, kicker, headline, summary, source,
                       x, yy, cw, ch)


def draw_map(d, items, pins):
    y = 626
    d.text((10, y), "WHERE IT HAPPENED — pins 1–16 numbered; dots are "
                    "stories 17–50", font=font(True, 12, True), fill=RED)
    rule(d, 10, y + 16, W - 10, width=2, fill=RED)
    mx0, my0, mx1, my1 = 10, 646, W - 10, 732
    d.rectangle([mx0, my0, mx1, my1], fill=SEA, outline=CARD_LINE)

    def proj(lon, lat):
        px = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
        py = my0 + (85.0 - lat) / 145.0 * (my1 - my0)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for num, text, lon, lat in items:
        px, py = proj(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(40, 40, 40))
    for num, (lon, lat) in sorted(pins.items()):
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        tw = d.textlength(label, font=font(True, 8, True))
        d.text((px - tw / 2, py - 6), label, font=font(True, 8, True),
               fill=(255, 255, 255))


def draw_list(d, items):
    y = 738
    d.text((10, y), "ALSO ON TUESDAY 24 NOVEMBER · 17–50",
           font=font(True, 12, True), fill=RED)
    rule(d, 10, y + 16, W - 10, width=2, fill=RED)
    cols = [items[i::4] for i in range(4)]
    cw = (W - 20 - 3 * 12) // 4
    bottom = 0
    for ci, col in enumerate(cols):
        x = 10 + ci * (cw + 12)
        yy = 760
        for num, text, _lon, _lat in col:
            line = "%d. %s" % (num, text)
            yy = block(d, x, yy, line, font(True, 8), cw, 9, INK,
                       max_lines=3)
            yy += 2
        bottom = max(bottom, yy)
    return bottom


def draw_footer(d):
    y = 960
    d.rectangle([10, y, W - 10, y + 50], fill=(232, 226, 210),
                outline=CARD_LINE)
    d.text((16, y + 4), "DATE CHECK", font=font(True, 11, True), fill=RED)
    block(d, 16, y + 18, DATE_CHECK, font(True, 8), W - 32, 10, INK,
          max_lines=3)
    d.text((10, 1014), SOURCES, font=font(True, 8), fill=GREY)


def render(variant):
    leads, grid, items, pins = VARIANTS[variant]
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_timeline(d)
    draw_leads(d, leads)
    draw_grid(d, grid)
    draw_map(d, items, pins)
    list_bottom = draw_list(d, items)
    draw_footer(d)
    return img, list_bottom


def main(argv):
    variant = argv[1] if len(argv) > 1 else "classic"
    out = argv[2] if len(argv) > 2 else "entry.png"
    if variant not in VARIANTS:
        raise SystemExit("unknown variant: %s" % variant)
    img, list_bottom = render(variant)
    img.save(out, format="PNG")
    print("wrote %s (list bottom %d, footer 960-1010)" % (out, list_bottom))
    if list_bottom > 958:
        print("WARNING: list overflows into footer")


if __name__ == "__main__":
    main(sys.argv)
