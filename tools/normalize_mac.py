#!/usr/bin/env python3
"""
Normalize a .MAC source file to the on-disk format expected by M80:
  - encoding: CP850 (the original TED sources are CP850, and M80 is byte-
    oriented, so any non-ASCII bytes must round-trip as CP850).
  - line endings: CRLF.
  - trailing CP/M Ctrl-Z (0x1A) EOF marker.

Usage: normalize_mac.py FILE [FILE...]

The file is read, decoded as UTF-8 (so Claude-authored translations work),
then re-emitted with CP850 encoding, CRLF endings, and a trailing 0x1A.
A leading BOM if present is stripped.

Idempotent: running it twice is the same as running it once.
"""
from __future__ import annotations
import sys
from pathlib import Path

CTRL_Z = b'\x1a'


def normalize_bytes(data: bytes) -> bytes:
    # Try UTF-8 first (the translation pipeline writes UTF-8); fall back
    # to CP850 so already-normalized files round-trip without changes.
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = data.decode('cp850')
    # Drop any pre-existing trailing Ctrl-Z so it's added back exactly once.
    text = text.rstrip('\x1a')
    # Drop trailing whitespace per line (M80 ignores it; keeps diffs clean).
    lines = [ln.rstrip() for ln in text.splitlines()]
    body = '\r\n'.join(lines)
    if not body.endswith('\r\n'):
        body += '\r\n'
    return body.encode('cp850') + CTRL_Z


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('usage: normalize_mac.py FILE [FILE...]', file=sys.stderr)
        return 2
    for arg in argv[1:]:
        p = Path(arg)
        out = normalize_bytes(p.read_bytes())
        p.write_bytes(out)
        print(f'normalized {p}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
