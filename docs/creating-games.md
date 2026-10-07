# Creating a minigame

## 1. Choose an example

Run the commands in the README. Start with `examples/pad-test/main.asm` for
RGBDS, `examples/c-pad/main.c` for the C diagnostic, or
[`examples/c-reaction/`](../examples/c-reaction/) for the reaction game.
REACTION has its own entry and header, sharing the C implementation and bridge
from C PAD: wait for GO, press A, and read the elapsed count in hexadecimal;
B restarts. Pressing A before GO shows TOO EARLY. Start+Select returns to the host.
Time is counted in iterations synchronized with frames, not milliseconds;
FF means saturation at 255. This example does not save records.

The build runs locally. Do not run `make push` for testing: the legacy publisher
uses an external database and requires its own configuration.

## 2. Understand the entry and header

The host maps the game's first window at `$4000-$5FFF` and calls its entry.
Preserve the host's return address and stack. In the examples, `$4000` contains
`JP $406F`; the word at +3 contains `$006F`. The program begins after the header.

| Payload offset | Contents used by the examples |
| --- | --- |
| +0 | JP to entry |
| +3 | entry minus `$4000`, little-endian word |
| +5 | number of **8 KiB** blocks, here 1 |
| +6/+7/+8 | category / genre / legacy field 1 |
| +9..+12 | four-byte ID, here G001 |
| +13 | append ID, word; here zero |
| +15 | zero-terminated title, bounded by +35 |
| +36 | zero-terminated description, bounded by +67 |
| +68 | title marker, FF |
| +109/+110 | little-endian additive checksum |
| +111 | example entry |

The meaning of unknown fields has not been confirmed. The legacy Maker uses
3B B3 instead of a checksum: the host has a path that accepts this marker.
The new build calculates the actual checksum over all declared bytes, excluding
only +109/+110.

The host charmap in `include/charmap.asm` is not ASCII: space is 10 and digits
start at 20. The PAD examples retain the validated fixture's ASCII text;
space 20 may disappear in host menus. The in-game font is independent.
For new titles displayed by the host renderer, use its charmap and repeat the
catalog validation and hash checks.

## 3. Memory and graphics

MBC6 has two independent 8 KiB windows: A `$4000-$5FFF` and B `$6000-$7FFF`.
RGBDS BANK[1] identifies a physical 16 KiB bank in the linked file; it is not
an MBC6 selector. These examples occupy only the A half.

Use WRAM bank 1 at D800..D80A for these examples' state. The C startup selects
bank 1 and restores SVBK on exit. C700 holds persistent host state; using it
for game variables has already corrupted the return to the menu. The rest of
WRAM has not been established as available for arbitrary applications.

The examples install their own font in VRAM, clear the map and attributes,
configure the CGB palette, and draw only while VRAM is accessible. The C example
turns the LCD off during VBlank and enables LCDC=91. Interrupts remain disabled
during the game; frame waiting polls LY. Do not use `HALT` with this model.

## 4. Input and exit

APIJoypad at 027C updates FF96 (held) and FF97 (pressed). Bits:
A=0, B=1, Select=2, Start=3, Right=4, Left=5, Up=6, Down=7.
`pressed` avoids repeatedly counting a held button. Read once per frame.

On exit, the examples wait until both Start and Select are released. They write
10 to C671 (legacy exit state), clear callbacks 0150/0153/0156/0159 with DE=0,
clear scroll/VBK, restore IE/STAT, and execute EI/RET. The C bridge also restores
SVBK. Do not jump to the cartridge reset vector.
This contract was validated with this host and these examples; it does not
establish compatibility with every game or physical hardware.

## 5. Package and prepare the server

`tools/package.py` takes the intermediate RGBDS image, extracts window A,
preserves the full block with zero padding, calculates the checksum, and calls
the original Maker compressor. Do not trim zeros: the host validates the declared
length; a partial final page may retain previous installer-buffer data.
The build rejects bytes outside the window and inconsistent headers/entries.

The wrapper contains: comment-length byte (0), reserved byte (0), mode (5),
compressed-length word, output-length word, two reserved bytes, and the stream
starting at +9. `bmvj_compress()` already returns this complete body; do not add
another envelope. Do not serve `.flash` as though it were `.cgb`.

For local REON, provide `0000.G001.cgb` and the fields from `game.json` to the
fixture process. The catalog schema observed in the host has four reserved bytes
before the usual fields; the encoder must follow REON's current contract.
The host performs GET followed by an authenticated POST with an empty body to
the same resource. A router that accepts only GET cannot complete the natural flow.

Test acquisition, BOX selection, writing, launch, controls, exit, relaunch in
the same core, and launch in a fresh core. The current release-wait examples
preserve BOX2. Earlier immediate-exit examples could trigger host list rebuilding
and move the game to BOX1; see [exit-release.md](exit-release.md) for the cause,
updated artifacts, and bounded validation.

## 6. Add features gradually

The declarations in `include/api/` document the Maker's register ABI.
Many were reconstructed statically: the presence of a symbol does not establish
its interaction with the game. The initial C integration covers only APIJoypad
and callback clearing on exit. Audio, files, skills, active callbacks, and
multi-block banking need their own examples and traces.
