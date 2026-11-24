#!/usr/bin/env python3
"""Deliver the 24 November 2026 front page to the grading folder.

build_poster.py draws the poster ahead of time and stores it in this
repository as assets/entry.png. This entry point only verifies that
stored file — PNG magic plus 1024x1024 dimensions — and copies the
identical bytes to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Pure standard library, no network, deterministic: the same bytes come
out on every run.
"""

import os
import struct
import sys
from pathlib import Path

WANT = (1024, 1024)
MAGIC = b"\x89PNG\r\n\x1a\n"
ASSET = "assets/entry.png"


def read_asset():
    root = Path(__file__).resolve().parent
    data = (root / ASSET).read_bytes()
    if data[:8] != MAGIC:
        raise SystemExit("%s is not a PNG file" % ASSET)
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != WANT:
        raise SystemExit("poster is %dx%d, want 1024x1024" % (w, h))
    return data


def ship(data):
    outdir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target = outdir / "entry.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print("wrote %s (%d bytes)" % (target, len(data)))


if __name__ == "__main__":
    ship(read_asset())
    sys.exit(0)
