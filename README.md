# msx2026

TED, an MSX2 word processor written by Ries (M.J.) Vriend in 1991, brought back to life in 2026 on [webmsx.org](https://webmsx.org). Plus the Microsoft M80/L80 toolchain it was built with, and a hello-world that proves the build/run loop on a 12-byte program.

## One-click launches

These open the online emulator and have it pull a ZIP-as-floppy straight from this repo's `dist/` over `raw.githubusercontent.com` — no install, no download, no drag-and-drop.

| What | Click | Time to first prompt |
|------|-------|----------------------|
| **Run prebuilt TED** (drops into the editor on `LEES.MIJ`) | [Launch](https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/ted-run.zip) | ~5 s |
| **Rebuild TED from source** (4× M80 + L80 + register + run) | [Launch](https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=MK&Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/ted-build.zip) | ~90 s |
| **Hello-world sanity check** (M80 → L80 → `Hello, MSX!`) | [Launch](https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=ML&DISKA_FILES_URL=https://raw.githubusercontent.com/riesvriend/msx2026/main/dist/hello-build.zip) | ~5 s |
| **Read the manual** | [doc/TED26.utf8.txt](doc/TED26.utf8.txt) — or inside TED with `BASIC_ENTER=TED+TED26.DOC` | — |

> Tip: If `raw.githubusercontent.com` ever blocks (rate limits, corporate proxy), download the zip from [`dist/`](dist/) and drag-drop it onto the WebMSX screen — same effect.

## How it works

WebMSX's `DISK` extension boots into MSX-DOS, accepts a ZIP via drag-drop or `?DISKA_FILES_URL=`, and auto-creates a 720 KB floppy from its contents. `M80` and `L80` are CP/M-80 binaries that run unchanged on MSX-DOS thanks to its CP/M BDOS compatibility, so the same pattern works for hello-world and for the full ~336 KB of TED source.

Each zip in `dist/` already contains `MSXDOS.SYS` + `COMMAND.COM` so the auto-built floppy boots to the MSX-DOS `A>` prompt instead of MSX BASIC.

## Editing locally

After changing a source file:

```bash
tools/pack.sh <target>     # tools | hello | ted | ted-run | all
git add dist/<target>.zip && git commit && git push
```

The launch URLs above always pick up the latest `main` of each zip.

## See also

The full walkthrough — including the registration step that lets a freshly built `TED.COM` actually start the editor — is captured as a question-driven skill at [.cursor/skills/run-ted-msx/SKILL.md](.cursor/skills/run-ted-msx/SKILL.md).
