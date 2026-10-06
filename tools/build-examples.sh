#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
kind="${1:-pad-test}"
out="$root/build/$kind"
mkdir -p "$out"
case "$kind" in
  pad-test)
    python3 tools/gen_font.py "$out/pad_font.inc"
    "${RGBDS:-}rgbasm" -I "$out/" -o "$out/main.o" examples/pad-test/main.asm
    ;;
  c-pad|c-reaction)
    cflags=(); aflags=()
    if [[ "$kind" == c-reaction ]]; then cflags=(-DREACTION); aflags=(-DREACTION); fi
    : "${GBDK_HOME:?Set GBDK_HOME to the GBDK 4.5.0 directory containing bin/lcc}"
    "$GBDK_HOME/bin/lcc" "${cflags[@]}" -K -no-crt -no-libs -Wl-b_CODE=0x4800 -Wl-b_DATA=0xD820 -Wl-m -Wl-w -o "$out/main.ihx" examples/c-pad/main.c examples/c-pad/link-symbols.s
    entry="$(python3 tools/c_extract.py "$out/main.ihx" "$out/main.map" "$out/c-code.bin")"
    "${RGBDS:-}rgbasm" "${aflags[@]}" -D C_ENTRY="$entry" -I "$out/" -o "$out/main.o" examples/c-pad/start.asm
    ;;
  *) echo 'Choose pad-test, c-pad or c-reaction' >&2; exit 2 ;;
esac
"${RGBDS:-}rgblink" -p 0 -o "$out/linked.gb" -n "$out/game.sym" "$out/main.o"
python3 tools/package.py "$out/linked.gb" "$out/game"
