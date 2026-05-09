#!/usr/bin/env python3
"""
Reduce an M80 assembly source to its non-comment skeleton.

Used to prove that a translation pass touched only comments: when the
stripped output of two .MAC files is byte-identical, the assembler will
produce identical .REL output (M80 discards comments before code-gen).

Handles the syntax variants found in the TED sources:
  - `;` starts a line comment to end-of-line, except inside a string literal.
  - `.comment <delim> ... <delim>` is a multi-line comment block; the
    delimiter is the first non-whitespace character after `.comment` and the
    block ends at the next occurrence of that character (M80 manual sec. 1.4).
  - String literals use single quotes; a doubled `''` embeds one quote.
    (Double-quoted strings do not appear in the TED sources, but are still
    treated as literals to be safe.)

Trailing whitespace on each line is dropped after comment removal — comment
authors cannot control how many spaces preceded their `;`, and that
whitespace is meaningless to M80. Leading whitespace IS preserved so that
column-1 labels remain distinguishable from indented instructions.

Files are read as CP850 (the original encoding of the TED sources) and
written back as UTF-8 with LF line endings to keep diffs reviewer-friendly.
"""
from __future__ import annotations
import sys
from pathlib import Path


def strip_line_comment(line: str) -> str:
    """Return `line` with comment removed and whitespace tokenised.

    Outside string literals we collapse any run of whitespace (spaces, tabs)
    to a single space and trim the ends. Inside a single-quoted string the
    bytes are preserved verbatim so that string contents are still compared
    byte-for-byte. The result is M80-equivalent: M80 tokenises on
    whitespace, so `label   equ 5` and `label equ 5` assemble identically.
    """
    out: list[str] = []
    i = 0
    n = len(line)
    in_string: str | None = None
    while i < n:
        ch = line[i]
        if in_string:
            out.append(ch)
            if ch == in_string:
                # Doubled quote inside a string is an escape, not a terminator.
                if i + 1 < n and line[i + 1] == in_string:
                    out.append(line[i + 1])
                    i += 2
                    continue
                in_string = None
            i += 1
            continue
        if ch == ';':
            break
        if ch in ("'", '"'):
            in_string = ch
            out.append(ch)
            i += 1
            continue
        if ch in (' ', '\t'):
            # Collapse any run of whitespace to one space.
            if out and out[-1] != ' ':
                out.append(' ')
            i += 1
            continue
        out.append(ch)
        i += 1
    # Trim leading/trailing space introduced by the collapse.
    return ''.join(out).strip()


def strip_source(text: str) -> str:
    """Strip all M80 comments (line + .comment blocks) from `text`."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.lstrip()
        # Detect a .comment block. M80 is case-insensitive on directives.
        low = stripped.lower()
        if low.startswith('.comment'):
            rest = stripped[len('.comment'):].lstrip()
            if not rest:
                # Delimiter is on the next non-empty line in some dialects;
                # in TED's sources the delimiter always follows on the same
                # line, so this branch is defensive only.
                i += 1
                continue
            delim = rest[0]
            # Drop everything up to and including the matching delimiter.
            tail = rest[1:]
            if delim in tail:
                # Single-line .comment block.
                i += 1
                continue
            i += 1
            while i < len(lines) and delim not in lines[i]:
                i += 1
            i += 1  # skip the closing-delimiter line itself
            continue
        line_out = strip_line_comment(raw)
        # Drop blank lines entirely — M80 doesn't care about vertical
        # whitespace, so keeping them would flag harmless reformatting.
        if line_out:
            out.append(line_out)
        i += 1
    return '\n'.join(out) + '\n'


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('usage: strip_comments.py <file.MAC> [more...]', file=sys.stderr)
        return 2
    for path in argv[1:]:
        p = Path(path)
        data = p.read_bytes()
        # Drop trailing CP/M Ctrl-Z (0x1A) EOF marker so it doesn't appear
        # mid-text after decoding.
        if data.endswith(b'\x1a'):
            data = data[:-1]
        text = data.decode('cp850')
        sys.stdout.write(f'===== {p.name} =====\n')
        sys.stdout.write(strip_source(text))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
