# net-de-get-maker

Project template for building Net de Get minigames. The original assembly
includes and legacy `make` workflow remain available.

## Start here

- [Guia de criação de jogos (Português)](docs/creating-games.md)
- [GBDK: integração experimental e limites](docs/gbdk.md)
- [Evidências e como repetir a validação](docs/validation.md)

Three original examples are available:

| Build | What it teaches |
| --- | --- |
| `pad-test` | RGBDS entry, direct graphics, eight buttons, host return |
| `c-pad` | The same diagnostic contract compiled in C with GBDK |
| `c-reaction` | A small playable reaction game in C: A reacts, B resets |

```sh
# Requires Python 3 and RGBDS (validated with 1.0.3).
tools/build-examples.sh pad-test

# GBDK_HOME contains bin/lcc; validated with official GBDK 4.5.0.
export GBDK_HOME=/path/to/gbdk
tools/build-examples.sh c-pad
tools/build-examples.sh c-reaction
```

Outputs go to `build/<example>/`: `game.flash` is an 8192-byte flash
payload; `0000.G001.cgb` is the compressed HTTP body. They are different formats.
`game.json` records header metadata and hashes. Each example uses fixture ID
G001: publish one at a time or assign distinct IDs before packaging.

These are host-loaded minigames, not standalone cartridge ROMs. Supply your own
legally obtained host ROM and disposable synthetic save fixtures outside Git.
No original ROM, real saves, credentials or server responses belong here.
