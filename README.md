# msx2026

TED, an MSX2 word processor written by Ries (M.J.) Vriend in 1991, brought back to life in 2026 on [webmsx.org](https://webmsx.org). Plus the Microsoft M80/L80 toolchain it was built with, and a hello-world that proves the build/run loop on a 12-byte program.

## Quick start

| What | How |
|------|-----|
| **Run prebuilt TED** | Open the [ted-run launch URL](https://webmsx.org/?MACHINE=MSX2PE&PRESETS=DISK,RAM512&FAST_BOOT=1&BASIC_ENTER=TED+LEES.MIJ) and drag `dist/ted-run.zip` onto the screen, or pass `&DISKA_FILES_URL=<your-zip-url>`. |
| **Rebuild TED from source** | Same launch but with `&DISKA_FILES_URL=<ted-build.zip>&BASIC_ENTER=MK&Z80_CLOCK_MODE=8&VDP_CLOCK_MODE=8`. The build runs automatically. |
| **Hello-world sanity check** | `&DISKA_FILES_URL=<hello-build.zip>&BASIC_ENTER=ML`. M80 → L80 → `Hello, MSX!`. |
| **Read the manual** | Open [doc/TED26.utf8.txt](doc/TED26.utf8.txt) — or inside TED itself, with `BASIC_ENTER=TED+TED26.DOC`. |

After editing a source file: `tools/pack.sh <target>` (`tools`, `hello`, `ted`, `ted-run`, or `all`).

Each zip already contains `MSXDOS.SYS` + `COMMAND.COM` so WebMSX's auto-built floppy boots to the MSX-DOS `A>` prompt.

## How it works

WebMSX's `DISK` extension boots into MSX-DOS, accepts a ZIP via drag-drop or `?DISKA_FILES_URL=`, and auto-creates a 720 KB floppy from its contents. `M80` and `L80` are CP/M-80 binaries that run on MSX-DOS thanks to its CP/M BDOS compatibility, so the same pattern works for hello-world and for the full ~336 KB of TED source.

## See also

The full walkthrough — including the registration step that lets a freshly built `TED.COM` actually start the editor — is captured as a question-driven skill at [.cursor/skills/run-ted-msx/SKILL.md](.cursor/skills/run-ted-msx/SKILL.md).
