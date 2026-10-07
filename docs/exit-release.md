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
