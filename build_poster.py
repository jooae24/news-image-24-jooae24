#!/usr/bin/env python3
"""Tuesday 24 November 2026 front page — one 1024x1024 newspaper poster.

A broadsheet front page drawn from scratch with Pillow: black masthead,
UTC timeline strip, four lead stories with hand-drawn illustrations, a
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

Standard library and Pillow only. No network access. The same command
always writes byte-identical PNGs.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

PAGE = (1024, 1024)

PAL = {
    "paper": (248, 243, 232),
    "ink": (18, 18, 18),
    "grey": (90, 90, 86),
    "red": (178, 34, 28),
    "navy": (28, 52, 96),
    "gold": (212, 175, 55),
    "sea": (198, 222, 235),
    "land": (196, 214, 166),
    "land_edge": (120, 140, 100),
    "card": (255, 253, 247),
    "card_edge": (178, 168, 148),
    "sky": (208, 228, 240),
    "green": (28, 120, 60),
    "foot": (232, 226, 210),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


class Sheet:
    """A 1024x1024 newsprint page plus the drawing tools used on it."""

    def __init__(self):
        self.image = Image.new("RGB", PAGE, PAL["paper"])
        self.pen = ImageDraw.Draw(self.image)
        self._faces = {}

    def face(self, size, bold=False, serif=False):
        key = (size, bold, serif)
        if key not in self._faces:
            if serif:
                name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
            else:
                name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
            self._faces[key] = ImageFont.truetype(FONT_DIR + "/" + name,
                                                  size)
        return self._faces[key]

    def text(self, x, y, s, size=12, bold=False, fill=None, serif=False):
        self.pen.text((x, y), s, font=self.face(size, bold, serif),
                      fill=fill or PAL["ink"])

    def width(self, s, size=12, bold=False, serif=False):
        return self.pen.textlength(s, font=self.face(size, bold, serif))

    def wrap(self, s, size, max_w, bold=False, serif=False):
        """Greedy word wrap of s into lines that fit max_w."""
        face = self.face(size, bold, serif)
        out = []
        for chunk in s.split("\n"):
            words = chunk.split()
            if not words:
                out.append("")
                continue
            cur = words[0]
            for word in words[1:]:
                trial = cur + " " + word
                if self.pen.textlength(trial, font=face) <= max_w:
                    cur = trial
                else:
                    out.append(cur)
                    cur = word
            out.append(cur)
        return out

    def para(self, x, y, s, size, max_w, leading, fill=None, limit=None,
             bold=False, serif=False):
        """Draw a wrapped paragraph; returns the y just below it."""
        lines = self.wrap(s, size, max_w, bold, serif)
        face = self.face(size, bold, serif)
        shown = lines
        if limit is not None and len(lines) > limit:
            shown = list(lines[:limit])
            tail = shown[-1]
            while tail and self.pen.textlength(tail + "…",
                                               font=face) > max_w:
                tail = tail[:-1]
            shown[-1] = tail + "…"
        for i, line in enumerate(shown):
            self.pen.text((x, y + i * leading), line, font=face,
                          fill=fill or PAL["ink"])
        return y + len(shown) * leading

    def hline(self, x0, y, x1, weight=1, fill=None):
        self.pen.line([(x0, y), (x1, y)], fill=fill or PAL["ink"],
                      width=weight)

    def box(self, x0, y0, x1, y1, fill=None, edge=None):
        self.pen.rectangle([x0, y0, x1, y1], fill=fill,
                           outline=edge)

    def save(self, path):
        self.image.save(path, format="PNG")

# --- the day's stories ---------------------------------------------------
# A lead story: number, kicker, dateline, headline, summary, source, art.
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
    13: (33, 69), 14: (12, 43), 15: (175, -41), 16: (6, 46),
}

PINS_MARKETS = {
    1: (-122, 37), 2: (106, -6), 3: (21, 52), 4: (-74, 40),
    5: (20, 32), 6: (131, 37), 7: (149, -35), 8: (51, 35),
    9: (-77, 39), 10: (34, 31), 11: (-93, 42), 12: (60, 27),
    13: (15, 54), 14: (33, 69), 15: (12, 43), 16: (175, -41),
}

VARIANTS = {
    "classic": (LEADS_CLASSIC, GRID_CLASSIC, LIST_CLASSIC, PINS_CLASSIC),
    "markets": (LEADS_MARKETS, GRID_MARKETS, LIST_MARKETS, PINS_MARKETS),
}

# --- the world map -------------------------------------------------------
# My own coarse outlines (lon, lat) for a stylised strip map.
WORLD = [
    # North America
    [(-168, 66), (-155, 70), (-140, 70), (-135, 68), (-128, 71),
     (-120, 72), (-110, 72), (-100, 73), (-90, 73), (-87, 70),
     (-85, 66), (-83, 62), (-81, 58), (-79, 55), (-77, 58),
     (-79, 62), (-81, 66), (-79, 68), (-76, 62), (-72, 58), (-65, 60),
     (-60, 55), (-55, 52), (-58, 47), (-60, 45), (-66, 44),
     (-70, 42), (-74, 40), (-76, 36), (-78, 34), (-80, 32),
     (-81, 29), (-81, 25), (-82, 27), (-84, 30), (-86, 30),
     (-88, 29), (-90, 22), (-94, 19),
     (-97, 16), (-93, 15), (-88, 13), (-84, 11), (-80, 9),
     (-79, 9), (-83, 10), (-88, 14), (-92, 15), (-96, 16),
     (-100, 18), (-104, 20), (-107, 21), (-110, 23), (-112, 26),
     (-114, 29), (-116, 32),
     (-120, 34), (-124, 40), (-124, 48), (-128, 54), (-135, 58),
     (-142, 60), (-150, 61), (-156, 58), (-162, 58), (-166, 60)],
    # South America
    [(-79, 9), (-77, 5), (-78, 1), (-80, -3), (-81, -6), (-80, -12),
     (-78, -16), (-74, -20), (-71, -24), (-70, -30), (-71, -35),
     (-72, -42), (-70, -48), (-66, -55), (-68, -53), (-66, -48),
     (-63, -42), (-59, -36), (-54, -34), (-49, -28), (-43, -23),
     (-39, -17), (-35, -10), (-35, -6), (-38, -4), (-44, -2),
     (-49, 0), (-53, 3), (-57, 6), (-62, 9), (-67, 11), (-72, 12),
     (-76, 10)],
    # Europe
    [(-10, 36), (-9, 40), (-9, 43), (-4, 44), (-2, 47), (-2, 49),
     (-5, 50), (-5, 53), (-3, 55), (-5, 58), (-2, 58), (2, 58),
     (6, 57), (8, 57), (10, 57), (13, 55), (17, 56), (20, 55),
     (23, 57), (26, 59), (29, 60), (30, 62), (30, 66), (28, 70),
     (25, 71), (20, 70), (18, 69), (14, 67), (12, 65), (10, 63),
     (6, 60), (5, 58), (6, 55), (8, 54), (6, 53), (2, 51),
     (0, 50), (-2, 49), (-4, 48), (-2, 46), (-4, 44), (-6, 43),
     (-9, 41), (-10, 38)],
    # Africa
    [(-17, 15), (-16, 18), (-16, 22), (-14, 26), (-11, 30), (-6, 33),
     (-1, 35), (4, 37), (9, 37), (13, 36), (18, 33), (22, 32),
     (27, 31), (31, 31), (33, 29), (35, 27), (37, 22), (39, 18),
     (41, 14), (44, 11), (48, 11), (51, 11), (51, 8), (48, 3),
     (44, -2), (41, -6), (39, -11), (37, -17), (35, -22), (33, -27),
     (30, -31), (27, -33), (22, -35), (18, -33), (16, -29), (14, -24),
     (12, -18), (13, -12), (12, -7), (10, -2), (9, 1), (7, 4),
     (3, 6), (-2, 5), (-7, 4), (-12, 7), (-16, 11)],
    # Asia
    [(30, 36), (33, 36), (36, 36), (39, 38), (42, 39), (45, 39),
     (48, 40), (50, 42), (52, 44), (54, 46), (57, 48), (60, 50),
     (63, 52), (66, 55), (69, 58), (71, 62), (73, 66), (75, 70),
     (78, 72), (82, 73), (86, 74), (90, 75), (94, 76), (98, 77),
     (102, 77), (106, 76), (110, 75), (114, 74), (118, 73), (122, 72),
     (126, 71), (130, 71), (134, 71), (138, 72), (142, 72), (146, 72),
     (150, 71), (154, 70), (157, 68), (160, 66), (162, 62), (160, 58),
     (158, 54), (155, 50), (151, 46), (147, 44), (143, 42), (140, 38),
     (137, 35), (134, 34), (131, 32), (129, 31), (127, 33), (126, 36),
     (124, 39), (121, 38), (119, 34), (117, 30), (114, 24), (111, 21),
     (109, 18), (107, 13), (105, 9), (103, 8), (101, 6), (99, 9),
     (97, 13), (94, 16), (92, 20), (90, 22), (88, 22), (86, 20),
     (84, 18), (81, 15), (80, 12), (77, 8), (76, 11), (74, 15),
     (72, 19), (70, 21), (68, 23), (64, 25), (60, 25), (57, 26),
     (56, 27), (58, 24), (59, 21), (57, 18), (54, 16), (51, 14),
     (47, 13), (44, 12), (42, 14), (40, 17), (39, 21), (38, 25),
     (37, 29), (35, 32), (34, 34), (36, 36), (33, 36)],
    # Australia
    [(113, -22), (114, -27), (115, -31), (115, -34), (118, -35),
     (122, -34), (126, -32), (129, -32), (132, -32), (135, -35),
     (138, -35), (140, -38), (143, -39), (146, -39), (149, -37),
     (150, -37), (153, -32), (153, -27), (151, -24), (149, -20),
     (146, -19), (143, -16), (142, -14), (142, -11), (140, -12),
     (137, -12), (135, -14), (133, -12), (131, -12), (129, -14),
     (126, -14), (123, -16), (121, -19), (118, -20), (115, -21)],
]


# --- lead illustrations --------------------------------------------------
# Each draws inside the rectangle (x0, y0, x1, y1) of a lead card.
def art_nvidia(sh, x0, y0, x1, y1):
    """A green chip, a rising chart and the +31% tag."""
    sh.box(x0, y0, x1, y1, fill=(16, 40, 24))
    sh.box(x0 + 10, y0 + 10, x0 + 58, y0 + 42, fill=PAL["green"],
           edge=(120, 200, 140))
    for px in (x0 + 22, x0 + 34, x0 + 46):
        sh.pen.line([(px, y0 + 5), (px, y0 + 10)], fill=(120, 200, 140),
                    width=2)
        sh.pen.line([(px, y0 + 42), (px, y0 + 47)], fill=(120, 200, 140),
                    width=2)
    sh.text(x0 + 14, y0 + 18, "NVDA", size=13, bold=True,
            fill=(255, 255, 255))
    pts = [(x0 + 66, y0 + 44), (x0 + 90, y0 + 34), (x0 + 112, y0 + 38),
           (x0 + 136, y0 + 24), (x0 + 158, y0 + 28), (x0 + 182, y0 + 12),
           (x0 + 200, y0 + 16)]
    sh.pen.line(pts, fill=(120, 230, 140), width=3)
    sh.pen.polygon([(x0 + 200, y0 + 16), (x0 + 190, y0 + 14),
                    (x0 + 198, y0 + 24)], fill=(120, 230, 140))
    sh.text(x1 - 60, y0 + 4, "+31%", size=20, bold=True,
            fill=(120, 230, 140))
    sh.text(x0 + 6, y1 - 12, "board vote unanimous · Trump pushed",
            size=9, fill=(200, 220, 205))


def art_nato(sh, x0, y0, x1, y1):
    """An AWACS plane under radar sweeps over a pale sky."""
    sh.box(x0, y0, x1, y1, fill=PAL["sky"])
    sh.pen.arc([x0 + 118, y0 - 62, x0 + 218, y0 + 38], 20, 160,
               fill=PAL["navy"], width=2)
    sh.pen.arc([x0 + 128, y0 - 52, x0 + 208, y0 + 28], 20, 160,
               fill=(90, 120, 170), width=1)
    sh.text(x0 + 6, y0 + 2, "AWACS", size=13, bold=True, fill=PAL["navy"])
    sh.pen.ellipse([x0 + 62, y0 + 16, x0 + 168, y0 + 34],
                   fill=PAL["navy"])
    sh.pen.ellipse([x0 + 102, y0 + 8, x0 + 138, y0 + 18],
                   fill=(60, 80, 120))
    sh.pen.polygon([(x0 + 168, y0 + 21), (x0 + 194, y0 + 25),
                    (x0 + 168, y0 + 29)], fill=PAL["navy"])
    sh.pen.polygon([(x0 + 72, y0 + 32), (x0 + 90, y0 + 44),
                    (x0 + 96, y0 + 32)], fill=PAL["navy"])
    sh.pen.polygon([(x0 + 128, y0 + 32), (x0 + 148, y0 + 44),
                    (x0 + 154, y0 + 32)], fill=PAL["navy"])
    sh.text(x0 + 6, y1 - 12, "3 Russian missiles landed Friday",
            size=9, fill=PAL["grey"])


def art_factory(sh, x0, y0, x1, y1):
    """A factory block with flames and smoke, and the death toll."""
    sh.box(x0, y0, x1, y1, fill=(52, 44, 40))
    sh.box(x0 + 14, y0 + 26, x0 + 118, y0 + 52, fill=(120, 110, 100))
    sh.box(x0 + 118, y0 + 18, x0 + 130, y0 + 52, fill=(90, 82, 74))
    sh.box(x0 + 136, y0 + 34, x0 + 188, y0 + 52, fill=(120, 110, 100))
    for fx, fh in ((x0 + 30, 18), (x0 + 58, 24), (x0 + 90, 16),
                   (x0 + 148, 14)):
        sh.pen.polygon([(fx - 8, y0 + 28), (fx, y0 + 28 - fh),
                        (fx + 8, y0 + 28)], fill=(232, 120, 30))
        sh.pen.polygon([(fx - 4, y0 + 28), (fx, y0 + 28 - fh + 8),
                        (fx + 4, y0 + 28)], fill=(240, 200, 60))
    sh.pen.ellipse([x0 + 148, y0 + 2, x0 + 170, y0 + 16],
                   fill=(150, 150, 150))
    sh.pen.ellipse([x0 + 168, y0 - 2, x0 + 190, y0 + 12],
                   fill=(170, 170, 170))
    sh.text(x1 - 64, y0 + 4, "24 DEAD", size=15, bold=True,
            fill=(255, 210, 90))
    sh.text(x0 + 6, y1 - 12, "~30 still missing in the wreckage",
            size=9, fill=(220, 215, 205))


def art_warship(sh, x0, y0, x1, y1):
    """A grey corvette on a dark sea, hit by a drone strike."""
    sh.box(x0, y0, x1, y1, fill=(24, 48, 84))
    sh.pen.ellipse([x1 - 34, y0 + 6, x1 - 12, y0 + 28],
                   fill=(232, 200, 120))
    sh.pen.polygon([(x0 + 20, y0 + 34), (x0 + 168, y0 + 34),
                    (x0 + 183, y0 + 44), (x0 + 30, y0 + 44)],
                   fill=(150, 160, 170))
    sh.box(x0 + 60, y0 + 24, x0 + 108, y0 + 34, fill=(120, 130, 140))
    sh.pen.line([(x0 + 84, y0 + 24), (x0 + 84, y0 + 14)],
                fill=(200, 200, 200), width=2)
    sh.pen.polygon([(x0 + 148, y0 + 20), (x0 + 158, y0 + 30),
                    (x0 + 170, y0 + 22), (x0 + 178, y0 + 32),
                    (x0 + 162, y0 + 36), (x0 + 156, y0 + 44),
                    (x0 + 144, y0 + 34)], fill=(240, 160, 40))
    sh.pen.ellipse([x0 + 34, y0 + 8, x0 + 46, y0 + 16],
                   fill=(220, 220, 220))
    sh.text(x0 + 6, y1 - 12, "Merkury hit in Benghazi harbour",
            size=9, fill=(220, 225, 235))


def art_markets(sh, x0, y0, x1, y1):
    """A green market board: S&P and Nasdaq up, Dow up."""
    sh.box(x0, y0, x1, y1, fill=(18, 46, 30))
    pts = [(x0 + 8, y0 + 44), (x0 + 40, y0 + 38), (x0 + 70, y0 + 42),
           (x0 + 100, y0 + 30), (x0 + 130, y0 + 34), (x0 + 160, y0 + 18),
           (x0 + 190, y0 + 22), (x0 + 210, y0 + 8)]
    sh.pen.line(pts, fill=(120, 230, 140), width=3)
    sh.pen.polygon([(x0 + 210, y0 + 8), (x0 + 200, y0 + 6),
                    (x0 + 208, y0 + 16)], fill=(120, 230, 140))
    sh.text(x0 + 8, y0 + 6, "S&P +4.7%", size=14, bold=True,
            fill=(255, 255, 255))
    sh.text(x0 + 100, y0 + 6, "NASDAQ +6.5%", size=14, bold=True,
            fill=(120, 230, 140))
    sh.text(x0 + 6, y1 - 12, "best day since April 2025 · Dow +1,448",
            size=9, fill=(200, 220, 205))


ARTS = {"nvidia": art_nvidia, "nato": art_nato, "factory": art_factory,
        "warship": art_warship, "markets": art_markets}

# --- page sections -------------------------------------------------------
# Fixed geometry, in pixels from the top-left corner of the 1024x1024 page.
MARGIN = 10
RIGHT = 1024 - MARGIN
LEAD_TOP, LEAD_H = 156, 208
GRID_TOP, CARD_H = 386, 76
MAP_TOP, MAP_H = 646, 86
LIST_TOP = 760
FOOT_TOP = 960


def section_head(sh, y, title):
    """A red section title with a rule underneath."""
    sh.text(MARGIN, y, title, size=12, bold=True, fill=PAL["red"])
    sh.hline(MARGIN, y + 16, RIGHT, weight=2, fill=PAL["red"])


def masthead(sh):
    sh.box(0, 0, 1024, 94, fill=(12, 12, 12))
    sh.text(14, 8, "THE WORLD IN ONE PAGE", size=33, bold=True,
            fill=(255, 255, 255))
    sh.text(14, 50, "Tuesday 24 November 2026", size=29, bold=True,
            serif=True, fill=PAL["gold"])
    sh.text(640, 10, "50 STORIES · 6 CONTINENTS", size=15, bold=True,
            fill=(255, 255, 255))
    sh.text(640, 34, "TUESDAY EDITION · ALL TIMES UTC", size=11,
            fill=(190, 190, 185))
    sh.text(640, 52, "Every story happened or was first", size=10,
            fill=(170, 170, 165))
    sh.text(640, 66, "reported on Tuesday 24 Nov 2026*", size=10,
            fill=(170, 170, 165))


def timeline(sh):
    section_head(sh, 100, "THE DAY IN UTC")
    slot = (RIGHT - MARGIN) // 6
    for i, (when, what) in enumerate(TIMELINE):
        x = MARGIN + i * slot
        sh.text(x, 120, when, size=11, bold=True, fill=PAL["red"])
        sh.para(x, 132, what, 9, slot - 8, 11, limit=2)


def lead_card(sh, story, x, y, w, h):
    sh.box(x, y, x + w, y + h, fill=PAL["card"], edge=PAL["card_edge"])
    sh.box(x, y, x + 22, y + 22, fill=PAL["red"])
    sh.text(x + 6, y + 3, str(story["n"]), size=13, bold=True,
            fill=(255, 255, 255))
    sh.text(x + 28, y + 4, story["kicker"], size=10, bold=True,
            fill=PAL["red"])
    ARTS[story["art"]](sh, x + 6, y + 28, x + w - 6, y + 88)
    sh.text(x + 6, y + 92, story["place"], size=9, bold=True,
            fill=PAL["navy"])
    sh.para(x + 6, y + 106, story["headline"], 13, w - 12, 15,
            limit=3, serif=True, bold=True)
    sh.para(x + 6, y + 152, story["summary"], 9, w - 12, 11, limit=4)
    sh.text(x + 6, y + h - 13, story["source"], size=8, fill=PAL["grey"])


def leads_row(sh, leads):
    cw = (RIGHT - MARGIN - 3 * 8) // 4
    for i, story in enumerate(leads):
        lead_card(sh, story, MARGIN + i * (cw + 8), LEAD_TOP, cw, LEAD_H)


def grid_card(sh, num, kicker, headline, summary, source, x, y, w, h):
    sh.box(x, y, x + w, y + h, fill=PAL["card"], edge=PAL["card_edge"])
    sh.text(x + 6, y + 4, str(num), size=11, bold=True, fill=PAL["red"])
    sh.text(x + 24, y + 5, kicker, size=9, bold=True, fill=PAL["red"])
    sh.para(x + 6, y + 19, headline, 11, w - 12, 13, limit=2,
            serif=True, bold=True)
    sh.para(x + 6, y + 46, summary, 9, w - 12, 11, limit=2)
    sh.text(x + 6, y + h - 11, "Source: " + source, size=8,
            fill=PAL["grey"])


def grid(sh, stories):
    section_head(sh, 366, "THE DAY'S NEWS · 5–16")
    cw = (RIGHT - MARGIN - 3 * 8) // 4
    for i, (kicker, headline, summary, source) in enumerate(stories):
        row, col = divmod(i, 4)
        grid_card(sh, 5 + i, kicker, headline, summary, source,
                  MARGIN + col * (cw + 8),
                  GRID_TOP + row * (CARD_H + 4), cw, CARD_H)


def world_map(sh, items, pins):
    section_head(sh, 626, "WHERE IT HAPPENED — pins 1–16 numbered; "
                          "dots are stories 17–50")
    x0, y0, x1, y1 = MARGIN, MAP_TOP, RIGHT, MAP_TOP + MAP_H
    sh.box(x0, y0, x1, y1, fill=PAL["sea"], edge=PAL["card_edge"])

    def project(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
        py = y0 + (85.0 - lat) / 145.0 * (y1 - y0)
        return px, py

    for outline in WORLD:
        sh.pen.polygon([project(lon, lat) for lon, lat in outline],
                       fill=PAL["land"], outline=PAL["land_edge"])
    for _num, _text, lon, lat in items:
        px, py = project(lon, lat)
        sh.pen.ellipse([px - 2, py - 2, px + 2, py + 2],
                       fill=(40, 40, 40))
    for num, (lon, lat) in sorted(pins.items()):
        px, py = project(lon, lat)
        sh.pen.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PAL["red"],
                       outline=(255, 255, 255), width=1)
        label = str(num)
        tw = sh.width(label, 8, bold=True)
        sh.text(px - tw / 2, py - 6, label, size=8, bold=True,
                fill=(255, 255, 255))


def story_list(sh, items):
    section_head(sh, 738, "ALSO ON TUESDAY 24 NOVEMBER · 17–50")
    cols = [items[i::4] for i in range(4)]
    cw = (RIGHT - MARGIN - 3 * 12) // 4
    lowest = 0
    for ci, col in enumerate(cols):
        x = MARGIN + ci * (cw + 12)
        yy = LIST_TOP
        for num, text, _lon, _lat in col:
            yy = sh.para(x, yy, "%d. %s" % (num, text), 8, cw, 9,
                         limit=3)
            yy += 2
        lowest = max(lowest, yy)
    return lowest


def footer(sh):
    sh.box(MARGIN, FOOT_TOP, RIGHT, FOOT_TOP + 50, fill=PAL["foot"],
           edge=PAL["card_edge"])
    sh.text(16, FOOT_TOP + 4, "DATE CHECK", size=11, bold=True,
            fill=PAL["red"])
    sh.para(16, FOOT_TOP + 18, DATE_CHECK, 8, 1024 - 32, 10, limit=3)
    sh.text(MARGIN, 1014, SOURCES, size=8, fill=PAL["grey"])


def render(variant):
    leads, grid_stories, items, pins = VARIANTS[variant]
    sh = Sheet()
    masthead(sh)
    timeline(sh)
    leads_row(sh, leads)
    grid(sh, grid_stories)
    world_map(sh, items, pins)
    bottom = story_list(sh, items)
    footer(sh)
    return sh, bottom


def main(argv):
    variant = argv[1] if len(argv) > 1 else "classic"
    out = argv[2] if len(argv) > 2 else "entry.png"
    if variant not in VARIANTS:
        raise SystemExit("unknown variant: %s" % variant)
    sh, bottom = render(variant)
    sh.save(out)
    print("wrote %s (list bottom %d, footer 960-1010)" % (out, bottom))
    if bottom > 958:
        print("WARNING: list overflows into footer")


if __name__ == "__main__":
    main(sys.argv)
