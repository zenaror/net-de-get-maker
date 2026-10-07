# Exit waits for button release

The C entry bridge and assembly PAD example wait until both Start and Select
are released before returning to the host. They poll APIJoypad (`027C`) with
interrupts disabled, then run the existing callback/register restoration and
return through the original host stack.

The original host checks held Select when entering its local menu. The earlier
immediate exit left `FF96=0C` at native A20 `4010`/`401D` and ROM0 `3E00`,
triggering catalog reconstruction. This could move games to BOX1 or restore
logically deleted entries whose bytes remained in flash.

## Bounded validation

On the candidate mGBA library SHA256
`0122452480576dd1942e932523f30a3e95ddc288fc94906184e1fe2b3fe8fbbc`, all three
examples were staged before boot in disposable copies of a naturally acquired
save. These tests validate normal host launch and execution, **not natural
installation of the new HTTP body**. ROM and saves remain outside Git.

The exit sequence was `12:3, 4:3, 0:300`: hold Start+Select, release Start while
keeping Select, then release both. Each example stayed in its exit bridge while
Select remained held, returned normally at host `517E` with SP `FFF6`, and
reached A20 `4010` with `FF96=00`. No ROM0 `3E00` reconstruction was traced.
Index/Box pairs `20 01 10 01 FF 00` and complete flash remained unchanged.
C PAD and assembly PAD counted all eight inputs before exit; REACTION launch
and exit were checked without asserting its full gameplay logic.

| Example | New payload SHA256 | New body SHA256 |
| --- | --- | --- |
| c-pad | `f91e5460d0c54c029fb4e8cde1d22f27d007c499eda1880ec6561a179b0e477a` | `b3cd44b784d9b96c03db32a1a1a588cf89f869a1a36992197aa640ee667006c3` |
| pad-test | `f6458a756b28c98d05bc9380ff02e4a3539af27569e6edc39079ea31cc92290f` | `6c539e76deff80b15883586c653506811a9ddcdd40ffa3fb702c959d0f06cc81` |
| c-reaction | `30019d1ef2f8cf14381a0104829a0ffe50c1300d6c0f57e1d053deca56ddd0fa` | `182b1ddb9a9ee24a0be0448932c8faa948ae10aa342734bcf043f587f6bbe32a` |

Local trace/report directories:

- `/tmp/netdeget-exit-wait-c-pad-vbitpl2i`.
- `/tmp/netdeget-exit-wait-pad-test-donth4w1`.
- `/tmp/netdeget-exit-wait-c-reaction-2li_jrmw`.

This branch does not replace the frozen server fixtures or published releases.
Natural download/compression delivery checks and hardware validation remain
separate follow-up work.

## Packaging compatibility follow-up

`tools/package.py --game-id Gddd` now assigns an ID before full-block checksum
and compression, so three examples can be served together without manual byte
editing. `fix.py` preserves every declared 8192-byte block, including padding
and the final nonzero byte; the historical trimming step could remove data.
The legacy database uploader also recalculates the checksum after assigning its
ID and rejects numeric IDs outside 0..999. Its database deployment was not
executed or validated here; the current REON administrative importer is the
preferred publication route.

Offline `tools/validation/payload.py` passed five tests covering declared
1/2/16-block extraction, padding/final-byte preservation, checksums, ID bounds
and malformed lengths. CLI ID packaging also reproduced the following sealed
HTTP fixtures byte-exact:

| ID / example | Payload SHA256 | Body SHA256 |
| --- | --- | --- |
| G001 / c-pad | `f91e5460d0c54c029fb4e8cde1d22f27d007c499eda1880ec6561a179b0e477a` | `b3cd44b784d9b96c03db32a1a1a588cf89f869a1a36992197aa640ee667006c3` |
| G002 / pad-test | `5e7859cf12b6859e33f9c0ac129b308871bb386abae22c1d437357e6c241bc69` | `1dd5bbeea71edb3284e6046666ce9a0e94c38d7b6e13d720ca3d7372505c7c76` |
| G003 / c-reaction | `2d222205fd99fa749003d1584ca5dd375c7ab81a3e090c5fe30b8735cfebddcc` | `bf4ed67fb984083c4adc84c3a43743b676d1e35dbf9e35b45813c1eafba742ac` |

The default legacy `make` now creates `bin/` before linking, so a fresh checkout
builds without a manually created output directory. Its template built to an
8192-byte payload with the expected additive checksum in this validation.

The raw extraction/checksum helper accepts 1..16 declared blocks; this does not
mean the current compressor can frame all those sizes. Mode5 has 16-bit decoded
and encoded length fields, so the current single-body compressor rejects decoded
sizes above 65535 bytes (at most seven whole 8192-byte blocks) and oversized
compressed streams. Eight-or-more-block delivery needs separately implemented
and naturally validated framing. The three one-block examples are unaffected.
A sixth offline test covers the rejected 65536-byte boundary.

The legacy `push.py` targets `bmvj_games` with MySQL `LOAD_FILE` and external
copies under `/var/lib/mysql/tmp`; it is **not** the current REON
`bmvj_custom_games`/opt-in administrative importer. Copy failures now raise and
loaded field lengths are checked before commit, but no legacy database run was
performed. Publish the validated `game.json`/HTTP body using the current importer.

## Updated offline driver and independent review

The driver reads all feature defines from the actual mGBA `flags.make`, uses
matching generated includes, verifies the executed runtime identity against
that library, and removes loader-path overrides for the child process. It now
expects BOX2 preservation and relaunch rather than the former accidental BOX1
reconstruction. Exit is tested with partial release (`12:3, 4:3, 0:300`).

All three examples passed against final core `431041ac6`, library SHA256
`785daae7d4440ef15bf3238a92c8b33d621d8b84f6aacf85bac102f336c2650f`, version
`0.11-feature/full_server-9343-431041ac6`, without dirty:
`/tmp/maker-natural-3ncd_avn`, `4rf2m3zf`, `tspw8xb1`.
Independent review repeated them successfully in
`/tmp/maker-natural-avz4z2_i`, `7vrr_utq`, `4awsw9ve` and reported no objections
to this follow-up. These are staged-payload tests, not HTTP installation claims.

## Natural HTTP installation on the shipped Linux library

**CONFIRMED (2026-10-06):** the mGBA owner repeated acquisition of G001 C PAD,
G002 assembly PAD and G003 REACTION through the original Net de Get and a local
REON harness, using the actual Linux release library from committed core
`431041ac6e264b119476d47ecf9ab96f03f11d54`, SHA256
`9d1c7aa87d5f82f13b78a19c85778b48ff3258f1c387291299e5045d150ca936`.
Run logs report `0.11-feature/full_server-9343-431041ac6`, without dirty.
All three installed 8192-byte payloads were independently compared here against
the sealed G001/G002/G003 fixtures and matched exactly; catalog records were
`10 01 FF 00` (BOX2). The owner verified catalog/body response hashes and
preservation of bytes outside each installed block.

| Example | Natural acquisition | Fresh-core checks |
| --- | --- | --- |
| C PAD G001 | `/tmp/mgba-netdeget-local-c87iafz3` | `/tmp/mgba-clean-61f28-gameplay-zefkbz34`: eight inputs, held/partial release, host return, BOX2 preservation |
| ASM PAD G002 | `/tmp/mgba-netdeget-local-m7rjn5ti` | `/tmp/mgba-clean-61f28-gameplay-g08xdd5b`: same checks |
| REACTION G003 | `/tmp/mgba-netdeget-local-pmb9jz1n` | `/tmp/mgba-maker-reaction-7cslycib`: WAIT, TOO EARLY, GO, RESULT, reset, held/partial-release exit |

Fresh-core runs preserved the full flash. The reports and payload snapshots
were inspected independently before integration. This supersedes the earlier
new-body-delivery pending status for these three specific artifacts. It does
not certify physical cartridges, arbitrary games or the legacy MySQL uploader.
REON prices are historical game metadata; REON does not implement billing.
