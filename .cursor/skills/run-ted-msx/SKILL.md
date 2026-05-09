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
│   └── pack.sh             Builds the dist/*.zip files
├── src/
│   ├── hello/              HELLO.MAC + ML.BAT — minimal proof of the toolchain
│   └── ted/                TED #2.6 source: MAIN/SUBTED/TEDSTR/GETPUT/OFFSET/TEDGRAB.MAC
│                           plus original ML*.BAT and our cleaner MK.BAT / SHORT.BAT
├── runtime/ted/            Prebuilt TED.COM + helpers + LEES.MIJ + manual
├── dist/                   Drag any of these onto webmsx.org (or use as DISKA_FILES_URL)
│   ├── m80-tools.zip
│   ├── hello-build.zip
│   ├── ted-build.zip
│   └── ted-run.zip
└── doc/
    ├── TED26.DOC           Original Dutch manual (CP850 + box-drawing chars)
    └── TED26.utf8.txt      Same, transcoded for modern editors
```

Verified working as of May 2026 against WebMSX 6.0.8.

## How do I run a hello-world build right now?

1. `tools/pack.sh hello` rebuilds `dist/hello-build.zip` from `src/hello/`.
2. Open

   ```
   https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=<your-zip-url>&FAST_BOOT=1&BASIC_ENTER=ML
   ```

   or for local testing with the wrapper server in this repo: `http://localhost:8765/wmsx/index.html?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=http://localhost:8765/dist/hello-build.zip&FAST_BOOT=1&BASIC_ENTER=ML`.
3. WebMSX boots into MSX-DOS 1.03, types `ML`, runs `M80 =HELLO/M/P` then `L80 HELLO,HELLO/N/E`.
4. After the build, type `HELLO` in the emulator → `Hello, MSX!`.

The hello-world `AUTOEXEC.BAT` chains the whole sequence automatically; that's the recommended pattern for any `.MAC` project.

## How do I rebuild TED.COM from source?

1. `tools/pack.sh ted` rebuilds `dist/ted-build.zip` (tools + sources + `MK.BAT` + `LEES.MIJ`).
2. Launch:

   ```
   https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=<your-zip-url>&FAST_BOOT=1&BASIC_ENTER=MK&Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8
   ```

3. `MK.BAT` runs the four M80 passes (TEDSTR, GETPUT, SUBTED, MAIN) then `L80 SUBTED,GETPUT,TEDSTR,MAIN,TED/N/E` — produces a fresh `TED.COM` (~30 KB).
4. The same batch then runs `TED 12345` to register the binary (see "Why does my freshly built TED exit immediately?"), then `TED LEES.MIJ` to launch the editor.

At 8x Z80 turbo a fresh build takes a few minutes (TED is ~336 KB of source spread over four `.MAC` files). The original developer's `ML4.BAT` is included for reference but doesn't run on stock MSX-DOS 1 (uses `>` redirection and custom `disint`/`enaint` utilities); use `MK.BAT` instead.

## How do I run TED without rebuilding?

1. `tools/pack.sh ted-run` rebuilds `dist/ted-run.zip` (prebuilt `TED.COM` + helpers + manual + sample text + `MSXDOS.SYS` + `COMMAND.COM`).
2. Launch:

   ```
   https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=<your-zip-url>&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ
   ```

3. The editor appears immediately with `LEES.MIJ` loaded.
4. Inside TED: `F7` for help, `F2` for settings, `F3` for system, `F4` for commands, `F5` for blocks. Status bar is in Dutch.

## Why does my freshly built TED exit immediately?

TED's `MAIN.MAC` declares its entry point as `codeer` (line ~7678), not the editor. `codeer` is a one-shot **registration** routine:

1. Reads a serial number from the command line (digits only; non-digits ignored).
2. Patches the `JP` instruction at 100h so it points to `ini` (the real editor).
3. Computes a checksum, XOR-encodes the intro string for anti-piracy, writes the entire image back to disk via MSX-DOS CREATE/RBWRITE.
4. `RST 0` (exit to MSX-DOS).

So a fresh-from-`L80` `TED.COM` must be run once with `TED <some-number>` before it functions as an editor. `MK.BAT` does this with `TED 12345`. The prebuilt `runtime/ted/TED.COM` was already registered by its original developer, so it works on first launch.

## How do I read the Dutch manual?

- **Modern editor:** open [doc/TED26.utf8.txt](../../doc/TED26.utf8.txt). Box-drawing chars become Unicode equivalents.
- **As intended (inside TED):** use `dist/ted-run.zip` and `BASIC_ENTER=TED+TED26.DOC`.
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

Push the repo to GitHub and use:

```
https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=https://raw.githubusercontent.com/<user>/msx2026/main/dist/ted-run.zip&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ
```

`raw.githubusercontent.com` is CORS-friendly. Arbitrary hosts may not be — drag-drop the zip onto the WebMSX page is the always-works fallback.

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

```bash
# 1. clone WebMSX once
git clone https://github.com/ppeccin/WebMSX ~/WebMSX

# 2. set up a unified test directory (CORS-enabled HTTP server)
mkdir -p /tmp/wmsx-test
ln -snf ~/WebMSX/release/stable/6.0/standalone /tmp/wmsx-test/wmsx
ln -snf <repo>/dist /tmp/wmsx-test/dist

# 3. start the server (script in this repo at /tmp/wmsx-test/serve.py)
python3 /tmp/wmsx-test/serve.py

# 4. open
http://localhost:8765/wmsx/index.html?MACHINE=MSX2PE&PRESETS=DISK,RAM512&DISKA_FILES_URL=http://localhost:8765/dist/ted-run.zip&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ
```

Webmsx.org is fine for everything except CORS-blocked private zip URLs.

## Repo conventions

- Source files: byte-identical copies of the originals from `~/msx/`. Keep CP850 + Ctrl-Z layout.
- `dist/*.zip` is generated, not hand-edited. Re-run `tools/pack.sh <target>` after any source change.
- WebMSX preset: always `MSX2PE` with `DISK,RAM512`. Add `Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8` for builds.
- `MSXDOS.SYS` + `COMMAND.COM` go in every zip; pack.sh handles this.
