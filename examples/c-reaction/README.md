# C REACTION

A one-block reaction game for Net de Get: wait for GO, press A, read the elapsed
frame count in hexadecimal, and press B to restart. Pressing A before GO shows
TOO EARLY. Start+Select exits after both buttons are released, preserving the
host's BOX organization. The game does not save records.

## Build

From the repository root, with RGBDS, Python 3 and GBDK 4.5.0 installed:

```sh
export GBDK_HOME=/path/to/gbdk
make c-reaction
# Equivalent: tools/build-examples.sh c-reaction
```

Outputs: `build/c-reaction/game.flash` (8192-byte decoded program),
`0000.G001.cgb` (HTTP body) and `game.json` (metadata/checksum/hashes).
Assign G003 for the three-example catalog using:

```sh
python3 tools/package.py build/c-reaction/linked.gb build/c-reaction/game --game-id G003
```

## Source organization

- [main.c](main.c) is this example's C entry and defines REACTION.
- [start.asm](start.asm) selects its header and shared host-return bridge.
- [Shared C implementation](../c-pad/main.c) contains the reaction state machine,
  input bridge, font rendering and C PAD diagnostics, selected at compile time.
- [Shared assembly bridge](../c-pad/start.asm) preserves the host stack/registers
  and waits for exit-button release.

Sharing these implementations avoids separate copies of the ABI and graphics
code. State bytes: D803 elapsed count, D804 state (0 WAIT, 1 GO, 2 RESULT,
3 TOO EARLY), D805 countdown; the time is frames, not milliseconds.

See [GBDK integration](../../docs/gbdk.md) and
[validation evidence](../../docs/exit-release.md). The same G003 payload was
naturally downloaded and tested with mGBA 431041ac6 and the original host.
This directory adds discoverability without changing that validated program.
No host ROM or save is included. Original example code/fonts use MIT licensing.
