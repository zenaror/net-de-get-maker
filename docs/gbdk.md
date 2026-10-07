# GBDK: experimental integration

## What works

GBDK-2020 4.5.0 compiles C for SM83 inside a host-loaded payload.
`c-pad` passed natural entry, all eight buttons, exit, and relaunch in the same
core. `c-reaction` passed a valid round, early input, reset, exit, and relaunch.
Consult the evidence matrix before extending these results to other cases.

This is an initial compiler integration. It is not a complete port of the
Maker SDK or the GBDK library to Net de Get.

## REACTION example

[`examples/c-reaction/`](../examples/c-reaction/) contains its own `main.c`,
`start.asm`, and README. `make c-reaction` builds this entry. It selects REACTION
and includes the shared C PAD implementation; the header does the same with the
assembly bridge. The programs and host contract remain identical to the validated
payloads, without duplicating ABI or graphics code.

## How the build works

1. `lcc -no-crt -no-libs` compiles without cartridge startup or standard libraries.
2. `_CODE` starts at 4800; the linker produces Intel HEX and a wide map.
3. `c_extract.py` rejects code outside 4800..5FFF and runtime areas with nonzero
   size. It copies code and constants to `c-code.bin` and locates `game_main`.
4. RGBDS assembles the header and bridge at 406F and includes C code at 4800.
5. `package.py` creates the payload, wrapper, and metadata offline.

`-K` skips lcc's cartridge checker; the extractor enforces the payload's own
limits. `link-symbols.s` declares references for the linker's default
_shadow_OAM/.STACK assignments, without allocating storage or executing code.
The program does not use those symbols, GBDK OAM, or SP=E000.

Globals use explicit `__at(D800...)` addresses and are initialized in `game_main`.
Do not add ordinary or initialized globals without implementing and validating
an initialization runtime: the build rejects those areas. Constants stay in
code. There is no heap, crt0, separate interrupt vector, or SP reset.

## ABI and runtime

Release 4.5.0 uses the default SM83 ABI, `__sdcccall(1)`. Do not cast 027C to a
C function pointer: the host API receives/returns registers under a different
contract. The naked `joypad()` function is an assembly bridge with no arguments;
it preserves BC, calls 027C, and returns. C reads the results from FF96/FF97.

The entry bridge preserves IE/STAT and SVBK on the host stack, executes DI,
selects WRAM1, calls C, clears callbacks, and returns to the original dispatcher.
It does not create a new stack. Keep nested calls shallow: natural reaction-game
samples observed SP=FFEE, returning to FFF6 in the menu; this does not establish
maximum consumption or a universal stack budget. Recursion and large local arrays
require a different stack strategy and validation.

Do not automatically use `printf`, `malloc`, `wait_vbl_done`, `add_VBL`, sprites,
audio, or ordinary GBDK banked functions: they assume their own globals/startup
and cartridge banking. A future callback bridge must respect the actual host
dispatcher convention and preserve registers; installing an `__interrupt`
function ending in RETI is insufficient. This has not yet been validated.

GBDK's usual 16 KiB banking does not directly model MBC6's two 8 KiB windows.
The current build rejects code beyond one block. A later step needs mapper
wrappers and far calls that preserve both windows.

## Reproduced toolchain

Official Linux x86_64 release: GBDK 4.5.0.
Archive `gbdk-linux64.tar.gz`, SHA256:
`d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c`.
RGBDS 1.0.3 and Python 3. No toolchain binaries are versioned here.

Primary sources:

- [Release 4.5.0](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.5.0)
- [Toolchain options](https://gbdk.org/docs/api/docs_toolchain_settings.html)
- [Migration and SDCC ABI](https://gbdk.org/docs/api/docs_migrating_versions.html)
- [GBDK usage guide](https://gbdk.org/docs/api/docs_using_gbdk.html)
