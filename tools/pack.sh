#!/usr/bin/env bash
# Rebuild a WebMSX-ready zip from on-disk sources.
#
# Each target produces a flat zip (no subdirectories) so MSX-DOS sees
# every file at A:\ when WebMSX auto-creates a floppy from the archive.
#
# Usage:
#   tools/pack.sh tools     -> dist/m80-tools.zip   (M80/L80/LIB80/CREF80)
#   tools/pack.sh hello     -> dist/hello-build.zip (tools + src/hello)
#   tools/pack.sh ted       -> dist/ted-build.zip   (tools + src/ted)
#   tools/pack.sh ted-run   -> dist/ted-run.zip     (runtime/ted + manual)
#   tools/pack.sh all       -> all of the above

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
mkdir -p "$DIST"

ensure_crlf() {
    # Convert LF-only text files to CRLF in place. Skip binaries (.COM, .REL).
    local f
    for f in "$@"; do
        case "$f" in
            *.COM|*.REL|*.com|*.rel) continue ;;
        esac
        if file "$f" | grep -q 'CRLF' ; then
            continue
        fi
        perl -pi -e 's/\r?\n/\r\n/g' "$f"
    done
}

pack_tools() {
    local out="$DIST/m80-tools.zip"
    rm -f "$out"
    (cd "$ROOT/tools/m80" && zip -j -q "$out" *.COM)
    echo "built $out"
}

add_msxdos() {
    # MSXDOS.SYS + COMMAND.COM make the auto-created floppy bootable.
    (cd "$ROOT/tools/msxdos" && zip -j -q "$1" MSXDOS.SYS COMMAND.COM)
}

pack_hello() {
    local out="$DIST/hello-build.zip"
    rm -f "$out"
    ensure_crlf "$ROOT"/src/hello/*.MAC "$ROOT"/src/hello/*.BAT
    add_msxdos "$out"
    (cd "$ROOT/tools/m80" && zip -j -q "$out" *.COM)
    (cd "$ROOT/src/hello" && zip -j -q "$out" *.MAC *.BAT 2>/dev/null || true)
    echo "built $out"
}

pack_ted() {
    local out="$DIST/ted-build.zip"
    rm -f "$out"
    ensure_crlf "$ROOT"/src/ted/*.MAC "$ROOT"/src/ted/*.BAT 2>/dev/null || true
    add_msxdos "$out"
    (cd "$ROOT/tools/m80" && zip -j -q "$out" *.COM)
    (cd "$ROOT/src/ted" && zip -j -q "$out" *.MAC *.BAT 2>/dev/null || true)
    (cd "$ROOT/runtime/ted" && zip -j -q "$out" LEES.MIJ 2>/dev/null || true)
    echo "built $out"
}

pack_ted_run() {
    local out="$DIST/ted-run.zip"
    rm -f "$out"
    add_msxdos "$out"
    (cd "$ROOT/runtime/ted" && zip -j -q "$out" $(ls 2>/dev/null) 2>/dev/null || true)
    echo "built $out"
}

target="${1:-}"
case "$target" in
    tools)    pack_tools ;;
    hello)    pack_hello ;;
    ted)      pack_ted ;;
    ted-run)  pack_ted_run ;;
    all)      pack_tools; pack_hello; pack_ted; pack_ted_run ;;
    ""|-h|--help)
        sed -n '2,16p' "$0"
        exit 1 ;;
    *)
        echo "unknown target: $target" >&2
        sed -n '2,16p' "$0"
        exit 1 ;;
esac
