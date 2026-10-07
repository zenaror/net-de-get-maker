# Validation and limits

## Current exit validation — 2026-10-06

The corrected exit waits until Start and Select are released before returning
to the host, preserving BOX2 organization. Current hashes and the G001, G002,
and G003 variants are listed in [exit-release.md](exit-release.md). The historical
section below retains the previous run's hashes and behavior; it does not
describe the new artifacts.

All three examples passed the updated `tools/validation/offline.py` with the
mGBA library from commit `431041ac6`, SHA256
`785daae7d4440ef15bf3238a92c8b33d621d8b84f6aacf85bac102f336c2650f`, version
`0.11-feature/full_server-9343-431041ac6`, without dirty. The driver uses all
C_DEFINES/generated build includes, verifies library identity, and checks
partial-release exit, BOX2 relaunch, and stable records and flash.
C/ASM PAD passed all eight inputs; REACTION passed WAIT, TOO EARLY, GO, RESULT,
and reset. Payloads staged before boot do not replace natural HTTP acquisition.

Evidence: `/tmp/maker-natural-3ncd_avn`, `4rf2m3zf`, and `tspw8xb1`.
Independent review repeated all three tests successfully in
`/tmp/maker-natural-avz4z2_i`, `7vrr_utq`, and `4awsw9ve`.
Six payload/checksum/ID and mode5 boundary tests passed; default `make` produced
8192 bytes with the correct checksum in a checkout without an existing `bin/`.
The legacy MySQL uploader was not executed; REON publication uses the current importer.

### Current HTTP acquisition

All three new examples passed natural download, byte-exact installation,
fresh-core execution, and exit preserving BOX2 with the Linux library selected
for distribution: core `431041ac6`, SHA256
`9d1c7aa87d5f82f13b78a19c85778b48ff3258f1c387291299e5045d150ca936`.
The hash table and report paths are in
[exit-release.md](exit-release.md#natural-http-installation-on-the-shipped-linux-library).
This run closes the pending delivery check for the new G001/G002/G003 bodies.
Price is historical metadata; REON has no billing system.

## Historical matrix before release-wait exit — 2026-10-06

| Example | Build | Natural entry, controls, exit, relaunch | HTTP download and fresh core |
| --- | --- | --- | --- |
| pad-test RGBDS | CONFIRMED, same hash as previous fixture | CONFIRMED | CONFIRMED in the previous mGBA run |
| c-pad GBDK | CONFIRMED | CONFIRMED | CONFIRMED: acquisition, writing, controls, exit, persistence |
| c-reaction GBDK | CONFIRMED | CONFIRMED: result, reset, early press, exit, and relaunch | Not tested |

CONFIRMED here requires observed execution. PROBABLE describes static
interpretation without a natural trace; HYPOTHESIS describes an explanation
still to be tested. Successful examples do not certify hardware, all games,
GBDK libraries, audio, game SRAM, or multi-bank operation. ROM reconstruction
remains outside the Maker's scope.

## Reproduced artifacts

| Build | Payload SHA256 (8192 bytes) | HTTP body SHA256 |
| --- | --- | --- |
| pad-test | `0e42875ef2569905d056f895ab5d6998e4f17709875dd27f13cbd9b20c2158b0` | `a8f6e181ddedf0f5d0b1b8e164d9e41edcddaadd14cf0c9f4730ede455560a24` |
| c-pad | `ab49fffb02e1b918d442a876508ed83c75ffc32fbbfa482cb8a3b9e46d70381c` | `f46337ae8627482742511c5d508aaa0ac66930de93c9fe2814fd0c00a02324ba` |
| c-reaction | `d8c75e797f41f144544680389dcf5516c9196e5a8602d65275471aa195656520` | `766b97107cb0d4d2ece60e6d21a5325e5707e7941a89736857628ccd2fd282ab` |

C PAD: `_CODE` 4800..4CE3, `game_main` 4AD0. Both enter through the header at 406F.
RGBDS 1.0.3 / GBDK 4.5.0. Host ROM SHA256:
`9fb1e6e4a637796b8624bd2de6c9abaa9e758546b620cb5dc8441b07c288bc63`.
Linux mGBA commit `358230c82773aec67dff2995eb77fbd84f8ea8a2`, library SHA256
`ee5795ed0eee7e0c4bd724dd73c490011d74e50af7b7bc1fe48b1079f033a29e`.

Temporary evidence from that session, kept outside Git:

- C PAD offline: `/tmp/netdeget-pad-natural-SMiyR7/run.log`.
- Offline reaction game after the visual correction: `/tmp/maker-natural-zwv7hotm/run.log`.
- Portable C PAD tester: `/tmp/maker-natural-e_ot118_/run.log`.
  State 01=GO; A recorded result 21 hexadecimal; B reset it, and early A
  produced state 03. After returning, the game reopened with state 00.

## Repeat the offline test

Provide your own ROM and a **synthetic** SRAM/flash fixture with game G001 in
the first block and BOX2 slot. The tester checks the format and uses copies in
a new temporary directory. Do not point it at real saves.

```sh
python3 tools/validation/offline.py c-pad "$ROM" "$MGBA_SOURCE" "$MGBA_BUILD" \
  "$SYNTHETIC_BOX2_SAVE" "$SYNTHETIC_FLASH"
# Replace c-pad with pad-test or c-reaction.
```

The driver uses only joypad input during execution; memory reads check state.
Flash staging happens before boot. The test checks return, relaunch, unchanged
flash, and the ROM hash. It does not test download. The macro is specific to
this fixture/menu and is not a universal controller.

## Repeat natural acquisition

The mGBA checkout provides `tools/mbc6/run_netdeget_local.py`. Use an SRAM
fixture with an empty catalog, disposable erased flash, and local REON with
the four-entry baseline catalog plus G001. Do not use personal credentials.

```sh
python3 "$MGBA_SOURCE/tools/mbc6/run_netdeget_local.py" "$ROM" "$MGBA_BUILD" \
  "$EMPTY_SYNTHETIC_SAVE" "$ERASED_SYNTHETIC_FLASH" build/c-pad/game.flash \
  --payload-sha256 ab49fffb02e1b918d442a876508ed83c75ffc32fbbfa482cb8a3b9e46d70381c \
  --body-sha256 f46337ae8627482742511c5d508aaa0ac66930de93c9fe2814fd0c00a02324ba \
  --catalog-sha256 d5323f206466632a447ceb68168175af5d8c6de66e441c9a58f7868c65e679e6
```

These options were published in mGBA commit
`280b62ffc2c5add122ddee843ec19d07d9174ad0`; check `--help` in the checkout used.
The macro and eight-counter assertions cover PAD, not the reaction game.
New variants need their own expectations, not just new hashes. The runner
creates local DNS on 8053 and uses REON on 8088; stop the fixtures when finished.

### C PAD HTTP run

CONFIRMED: natural GET+POST acquisition, an exact 437-byte catalog and 1114-byte
wrapper; BOX2 selection and writing the entire payload; all eight input bits,
release, Start+Select, BOX1 item16, and reentry with zeroed counters.
In a fresh core: entry, A, release, exit, and unchanged flash. The remaining
flash, hidden/protection state, and ROM matched their baselines.

Evidence from the mGBA chat: `/tmp/mgba-netdeget-local-e964hi6b/run.log` and
`/tmp/mgba-netdeget-local-e964hi6b/reopened/run.log`. REON used an isolated local
fixture; no production data was needed.

### C PAD run against production REON

CONFIRMED on 2026-10-06: the mGBA chat ran the same C PAD against production
REON, using real DNS on port 53 and ordinary sockets, without a loopback server.
Acquisition through the original host, storage of 8192 bytes, all eight controls
and releases, exit, relaunch with cleared state, and fresh-core execution passed.
The remaining flash matched the baseline, and fresh-core launch did not alter
flash. The tested runtime remains 358230c82; the payload and wrapper hashes on
this page are unchanged.

Evidence kept outside Git:
`/tmp/mgba-netdeget-production-zqeg16la/run.log`,
`/tmp/mgba-netdeget-production-zqeg16la/reopened/run.log`, and
`/tmp/mgba-netdeget-production-zqeg16la/c-pad-controls.png`.
The REON owner corroborated catalog/body requests and deployed G001 as free
opt-in content with MIT attribution. Synthetic accounts and credentials used
in this run are not published in this repository.

This production evidence covers C PAD; the reaction game was validated only
offline in that historical run. It does not extend coverage to hardware or the
standard GBDK runtime. See the current section above for the later natural
acquisition checks on all three updated examples.
