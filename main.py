#!/usr/bin/env python3
"""Ship the 24 November 2026 front page to the grader's output folder.

The poster is rendered ahead of time by build_poster.py and stored in
this repository at assets/entry.png. This entry point only reads those
bytes back, confirms the PNG header says 1024x1024, and writes the
identical bytes to /output/entry.png. Standard library only, no
network, and the same bytes on every run.
"""
import os
import struct
import sys
from pathlib import Path

SIZE = (1024, 1024)
MAGIC = b"\x89PNG\r\n\x1a\n"


def entry_bytes():
    here = Path(__file__).resolve().parent
    blob = (here / "assets" / "entry.png").read_bytes()
    if blob[:8] != MAGIC:
        raise SystemExit("assets/entry.png is not a PNG file")
    width, height = struct.unpack(">II", blob[16:24])
    if (width, height) != SIZE:
        raise SystemExit("poster is %dx%d, want 1024x1024" % (width, height))
    return blob


def main():
    blob = entry_bytes()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = Path(outdir) / "entry.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    print("wrote %s (%d bytes)" % (dest, len(blob)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
