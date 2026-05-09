#!/usr/bin/env python3
"""Expand TED-style tabs to spaces, using the ruler stored in a .TED file.

This mirrors the MAKESP routine in src/ted/GETPUT.MAC, which is the
in-memory expansion path TED uses when reading a file with the F2/T/L
("Laad Tab-tekens direkt van disk") option turned OFF: each TAB byte
gets replaced with enough spaces to advance the destination column to
the next tab stop in the ruler. The ruler comes from the matching
*.TED settings file and is shared by all of TED's own source files
(stops at columns 0, 16, 40, then every 8 up to 248).

Usage:
    python3 tools/expand-ted-tabs.py SRC.MAC RULER.TED [DST]

If DST is omitted, SRC is overwritten in place. Bytes are passed
through as-is (the format is CP850 + 0x1A EOF) so the result remains a
valid MSX-DOS text file.
"""
from __future__ import annotations

import sys
from pathlib import Path

RULER_OFFSET = 103
RULER_LENGTH = 256


def read_ruler(ted_path: Path) -> list[int]:
    data = ted_path.read_bytes()
    if len(data) < RULER_OFFSET + RULER_LENGTH:
        raise SystemExit(f"{ted_path}: too small to contain a ruler")
    ruler = data[RULER_OFFSET : RULER_OFFSET + RULER_LENGTH]
    stops = [c for c, b in enumerate(ruler) if b == 0x2B]
    if not stops:
        raise SystemExit(f"{ted_path}: no '+' stops found at offset {RULER_OFFSET}")
    return stops


def expand_line(line: bytes, stops: list[int]) -> bytes:
    out = bytearray()
    col = 0
    for byte in line:
        if byte == 0x09:
            next_stop = next((s for s in stops if s > col), None)
            if next_stop is None:
                out.append(0x20)
                col += 1
            else:
                spaces = next_stop - col
                out.extend(b" " * spaces)
                col = next_stop
        else:
            out.append(byte)
            col += 1
    return bytes(out)


def expand_file(src: Path, stops: list[int]) -> bytes:
    raw = src.read_bytes()
    out = bytearray()
    for line in raw.split(b"\r\n"):
        out.extend(expand_line(line, stops))
        out.extend(b"\r\n")
    if not raw.endswith(b"\r\n"):
        del out[-2:]
    return bytes(out)


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 4):
        print(__doc__, file=sys.stderr)
        return 2
    src = Path(argv[1])
    ted = Path(argv[2])
    dst = Path(argv[3]) if len(argv) == 4 else src
    stops = read_ruler(ted)
    new = expand_file(src, stops)
    old_size = src.stat().st_size
    dst.write_bytes(new)
    print(
        f"{src} ({old_size} B) -> {dst} ({len(new)} B); "
        f"ruler stops: {stops[:6]}... ({len(stops)} total)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
