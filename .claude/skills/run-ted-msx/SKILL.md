---
name: run-ted-msx
description: Build and run TED (a 1991 Dutch MSX2 word processor) and other MSX/Z80 M80 assembly projects on webmsx.org. Use when the user mentions TED, MSX, M80, L80, MSX-DOS, webmsx, .MAC files, or wants to assemble or run Z80 .COM programs in the browser.
---

# Run And Build TED On webmsx.org

A question-driven walkthrough. The build/run loop runs in the browser via [webmsx.org](https://webmsx.org) (or a local clone of `~/WebMSX`). Host side just packs zips with `tools/pack.sh`; WebMSX auto-creates a 720K floppy from the zip when given `?DISKA_FILES_URL=...zip`.

## What's in this repo?

```
msx2026/
├── tools/
│   ├── m80/                M80.COM, L80.COM, LIB80.COM, CREF80.COM (CP/M-80 binaries)
│   ├── msxdos/             MSXDOS.SYS + COMMAND.COM — make any zip-disk bootable
│   ├── pack.sh             Builds the dist/*.zip files
│   └── expand-ted-tabs.py  Replays MAKESP from GETPUT.MAC to expand TAB → spaces
├── src/
│   ├── hello/              HELLO.MAC + ML.BAT — minimal proof of the toolchain
│   └── ted/                TED #2.6 source: MAIN/SUBTED/TEDSTR/GETPUT/OFFSET/TEDGRAB.MAC
│                           plus *.TED ruler files and our MK.BAT / SHORT.BAT
├── runtime/ted/            Prebuilt TED.COM + helpers + LEES.MIJ + manuals (Dutch + English)
├── dist/                   Drag any of these onto webmsx.org (or use as DISKA_FILES_URL)
│   ├── m80-tools.zip
│   ├── hello-build.zip
│   ├── ted-build.zip
│   └── ted-run.zip
└── doc/
    ├── TED26.DOC           Original Dutch manual (CP850 + box-drawing chars)
    ├── TED26.utf8.txt      Same, transcoded for modern editors
    ├── TED26ENG.DOC        English translation (CP850, opens inside TED)
    └── TED26ENG.utf8.txt   English translation, transcoded for modern editors
```

Verified working as of May 2026 against WebMSX 6.0.8.

## How do I run a hello-world build right now?

The repo is published. Just click:

```
https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=ML&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/hello-build.zip
```

What happens:
1. WebMSX fetches `hello-build.zip` from `raw.githubusercontent.com` and turns it into a 720K virtual floppy in drive A.
2. `MSXDOS.SYS` + `COMMAND.COM` are in the zip, so it boots to `A>`.
3. `AUTOEXEC.BAT` runs `M80 =HELLO/M/P` then `L80 HELLO,HELLO/N/E`, runs `HELLO` (`Hello, MSX!`), then `DIR HELLO.COM`.
4. Then `BASIC_ENTER=ML` invokes `ML.BAT` again as a re-build sanity check.

For local iteration: `tools/pack.sh hello` rebuilds `dist/hello-build.zip`. With a CORS-enabled local server: `http://localhost:8765/wmsx/index.html?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=http://localhost:8765/dist/hello-build.zip&FAST_BOOT=1&BASIC_ENTER=ML`. The `AUTOEXEC.BAT` pattern is what you want to copy for any new `.MAC` project.

## How do I rebuild TED.COM from source?

Click:

```
https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=MK&Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/ted-build.zip
```

What `MK.BAT` does:

1. `M80 =TEDSTR/M/P`, `M80 =GETPUT/M/P`, `M80 =SUBTED/M/P`, `M80 =MAIN/M/P` — assembles all four modules.
2. `L80 SUBTED,GETPUT,TEDSTR,MAIN,TED/N/E` — links them into a fresh `TED.COM` (~30 KB).
3. `TED 12345` — runs the freshly linked binary's registration entry point (see "Why does my freshly built TED exit immediately?"). This patches `TED.COM` on disk to make the editor reachable.
4. `TED LEES.MIJ` — launches the now-editorial `TED.COM` with the welcome letter open.

At 8x Z80 turbo the full sequence takes ~90 s in a foreground browser tab. The original developer's `ML4.BAT` is included for reference but doesn't run on stock MSX-DOS 1 (uses `>` redirection and custom `disint`/`enaint` utilities) — use `MK.BAT` instead.

For local iteration: `tools/pack.sh ted` rebuilds `dist/ted-build.zip` (tools + sources + `MK.BAT` + `LEES.MIJ`). Push to GitHub → next click of the URL above picks it up.

## How do I run TED without rebuilding?

Click:

```
https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/ted-run.zip
```

`dist/ted-run.zip` contains the already-registered prebuilt `TED.COM` plus `LEES.MIJ`, the manual, helpers, and `MSXDOS.SYS` + `COMMAND.COM`. The editor appears within seconds. Inside TED: `F7` help, `F2` settings, `F3` system, `F4` commands, `F5` block ops. Status bar is in Dutch.

Local iteration: `tools/pack.sh ted-run`.

## Why don't the .MAC sources have any TAB characters?

They used to. TED's editor stores tabs as ASCII 9 in memory and on disk (when F2/T/B "Bewaar Tab-tekens op diskette" is on), and when displaying or loading it expands them using a configurable ruler from a per-file `.TED` settings file. For TED's own sources that ruler has stops at columns **0, 16, 40, then every 8 up to 248** — labels at col 0, opcodes at col 16, comments at col 40. Modern viewers (GitHub, VS Code) default to 4- or 8-column tabs, which mangles the layout.

`tools/expand-ted-tabs.py` re-implements the `MAKESP` routine from `src/ted/GETPUT.MAC` byte for byte: it reads the ruler from a `.TED` file (offset 103, 256-byte column map, `0x2B` = stop) and replaces every `\t` with the right run of spaces. Run it after editing any source:

```bash
python3 tools/expand-ted-tabs.py src/ted/MAIN.MAC src/ted/MAIN.TED
```

The expanded files still assemble identically (same `TED.COM` bytes from `M80`/`L80`); they're just easier to read on github.com. Don't paste tab characters back into the sources — keep them space-only.

## Why does my freshly built TED exit immediately?

TED's `MAIN.MAC` declares its entry point as `codeer` (line ~7678), not the editor. `codeer` is a one-shot **registration** routine:

1. Reads a serial number from the command line (digits only; non-digits ignored).
2. Patches the `JP` instruction at 100h so it points to `ini` (the real editor).
3. Computes a checksum, XOR-encodes the intro string for anti-piracy, writes the entire image back to disk via MSX-DOS CREATE/RBWRITE.
4. `RST 0` (exit to MSX-DOS).

So a fresh-from-`L80` `TED.COM` must be run once with `TED <some-number>` before it functions as an editor. `MK.BAT` does this with `TED 12345`. The prebuilt `runtime/ted/TED.COM` was already registered by its original developer, so it works on first launch.

## How do I read the manual?

- **Modern editor (English):** open [doc/TED26ENG.utf8.txt](../../../doc/TED26ENG.utf8.txt). Box-drawing chars become Unicode equivalents.
- **Modern editor (Dutch original):** open [doc/TED26.utf8.txt](../../../doc/TED26.utf8.txt).
- **As intended (inside TED):** use `dist/ted-run.zip` and `BASIC_ENTER=TED+TED26ENG.DOC` (or `TED26.DOC` for Dutch). Both ship in `runtime/ted/`.
- **Print path the manual itself recommends:** open in TED, `F4`, `P`.

## How do I add a new .MAC project?

1. `mkdir -p src/myproj` and add `MYPROG.MAC` plus an `AUTOEXEC.BAT`:

   ```
   M80 =MYPROG/M/P
   L80 MYPROG,MYPROG/N/E
   MYPROG
   ```

2. Add a `pack_myproj()` to `tools/pack.sh` that follows the same shape as `pack_hello()` (always include `MSXDOS.SYS` + `COMMAND.COM` from `tools/msxdos/`).
3. `tools/pack.sh myproj`, launch with `?DISKA_FILES_URL=...&FAST_BOOT=1` — `AUTOEXEC.BAT` runs automatically when MSX-DOS boots.

Keep filenames 8.3 and uppercase. Use CRLF line endings (the `pack.sh` `ensure_crlf` step does this). Don't strip the CP/M `Ctrl-Z` (`0x1A`) EOF marker that's at the end of the original `.MAC`/`.BAT` files.

## How do I distribute the launch URL to others?

Already done: this repo is public at `github.com/riesvriend/msx2026`, and `raw.githubusercontent.com` is CORS-friendly to `webmsx.org`. The three one-click URLs in [README.md](../../../README.md) work for anyone with a browser. They were verified end-to-end on May 9 2026 against WebMSX 6.0.8.

For your own fork, replace `riesvriend` with your GitHub username:

```
https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ&DISKA_FILES_URL=https://raw.githubusercontent.com/<user>/msx2026/main/dist/ted-run.zip
```

Arbitrary other hosts may not have CORS — drag-drop the zip onto the WebMSX page is the always-works fallback.

## Why does my zip boot to MSX BASIC instead of A>?

The `DISK` extension only provides the floppy interface — to actually drop into MSX-DOS the disk needs `MSXDOS.SYS` and `COMMAND.COM` in its root. `pack.sh` adds these from `tools/msxdos/` to every zip it builds. Without them you land in Disk BASIC (`Disk BASIC version 1.0`) at the MSX BASIC `Ok` prompt.

## What URL parameters matter?

| Param | Why |
|-------|-----|
| `MACHINE=MSX2PE` | European MSX2+ (PAL 50Hz). TED targets MSX2; MSX2+ runs the same code with more RAM. |
| `PRESETS=DISK,RAM512` | Floppy interface + 512 KB RAM mapper. Plenty for TED. |
| `DISKA_FILES_URL=...zip` | WebMSX builds a 720K floppy from this zip and inserts in drive A. |
| `FAST_BOOT=1` | Skips the boot animation. |
| `BASIC_ENTER=ML` | After power-on, types the string + Enter. Works at MSX-DOS A> too, not only BASIC. |
| `Z80_CLOCK_MODE=8` | 8x Z80 speed — makes M80/L80 builds tractable. |
| `VDP_CLOCK_MODE=8` | 8x VDP — speeds up screen scrolling during M80's verbose output. |

## What if M80 errors with "?Command error" or "Bad command or file name"?

- `?Command error` from COMMAND.COM means MSX-DOS 1 didn't understand the line. Most common causes: `>` output redirection or `|` pipes (only in MSX-DOS 2), or `ECHO` (no built-in in MSX-DOS 1 — write your message to a `.TXT` file or just remove it).
- `Bad command or file name` means the executable isn't on the disk. Check the zip contents (`unzip -l dist/foo.zip`) and ensure filenames are uppercase 8.3.

## How do I run this entirely locally (no internet)?

Both `wmsx/` and `dist/` are served from the same `localhost:8765` origin, so CORS doesn't apply and stdlib `http.server` is enough — no custom server script needed.

```bash
# 1. clone WebMSX once
git clone https://github.com/ppeccin/WebMSX ~/WebMSX

# 2. set up a unified test directory side-by-side with the repo
mkdir -p /tmp/wmsx-test
ln -snf ~/WebMSX/release/stable/6.0/standalone /tmp/wmsx-test/wmsx
ln -snf "$(pwd)/dist"                          /tmp/wmsx-test/dist

# 3. serve it
python3 -m http.server 8765 --directory /tmp/wmsx-test

# 4. open
http://localhost:8765/wmsx/index.html?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=http://localhost:8765/dist/ted-run.zip&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ
```

Webmsx.org is fine for everything except CORS-blocked private zip URLs.

## Repo conventions

- Source files: byte-identical copies of the originals from `~/msx/`. Keep CP850 + Ctrl-Z layout.
- `dist/*.zip` is generated, not hand-edited. Re-run `tools/pack.sh <target>` after any source change.
- WebMSX preset: always `MSX2PE` with `DISK,RAM512`. Add `Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8` for builds.
- `MSXDOS.SYS` + `COMMAND.COM` go in every zip; pack.sh handles this.
