# Validação e limites

## Validação atual da saída — 2026-10-06

A saída corrigida espera Start e Select serem liberados antes do retorno ao
host, preservando a organização BOX2. Os hashes atuais e as variantes G001,
G002 e G003 estão em [exit-release.md](exit-release.md). A seção histórica
abaixo conserva os hashes e o comportamento da rodada anterior; não descreve
os novos artefatos.

Os três exemplos passaram em `tools/validation/offline.py` atualizado com a
biblioteca mGBA do commit `431041ac6`, SHA256
`785daae7d4440ef15bf3238a92c8b33d621d8b84f6aacf85bac102f336c2650f`, versão
`0.11-feature/full_server-9343-431041ac6`, sem dirty. O driver usa todas as
C_DEFINES/includes geradas do build, verifica a identidade da biblioteca e
confere saída com liberação parcial, reentrada BOX2, registros e flash estáveis.
C/ASM PAD passaram oito inputs; REACTION passou WAIT, TOO EARLY, GO, RESULT e
reset. Payloads preparados antes do boot não substituem aquisição HTTP natural.

Evidências: `/tmp/maker-natural-3ncd_avn`, `4rf2m3zf` e `tspw8xb1`.
Revisão independente repetiu os três testes com sucesso em
`/tmp/maker-natural-avz4z2_i`, `7vrr_utq` e `4awsw9ve`.
Seis testes de payload/checksum/ID e limites de mode5 passaram; `make` padrão
produziu 8192 bytes e checksum correto em checkout sem `bin/` prévio.
O uploader MySQL legado não foi executado; publicação REON usa o importer atual.

## Histórico: matriz anterior à espera de liberação — 2026-10-06

| Exemplo | Build | Entrada natural, controles, saída, reabertura | Download HTTP e core novo |
| --- | --- | --- | --- |
| pad-test RGBDS | CONFIRMED, mesmo hash da fixture anterior | CONFIRMED | CONFIRMED na rodada anterior do mGBA |
| c-pad GBDK | CONFIRMED | CONFIRMED | CONFIRMED: aquisição, escrita, controles, saída, persistência |
| c-reaction GBDK | CONFIRMED | CONFIRMED: resultado, reset, early press, saída e reabertura | Não testado |

CONFIRMED aqui exige execução observada. PROBABLE descreve interpretação estática
sem trace natural; HYPOTHESIS descreve uma explicação ainda por testar.
O sucesso dos exemplos não certifica hardware, todos os jogos, bibliotecas GBDK,
áudio, SRAM de jogos ou banking múltiplo. A reconstrução da ROM permanece fora
do escopo.

## Artefatos reproduzidos

| Build | SHA256 do payload (8192 bytes) | SHA256 do corpo HTTP |
| --- | --- | --- |
| pad-test | `0e42875ef2569905d056f895ab5d6998e4f17709875dd27f13cbd9b20c2158b0` | `a8f6e181ddedf0f5d0b1b8e164d9e41edcddaadd14cf0c9f4730ede455560a24` |
| c-pad | `ab49fffb02e1b918d442a876508ed83c75ffc32fbbfa482cb8a3b9e46d70381c` | `f46337ae8627482742511c5d508aaa0ac66930de93c9fe2814fd0c00a02324ba` |
| c-reaction | `d8c75e797f41f144544680389dcf5516c9196e5a8602d65275471aa195656520` | `766b97107cb0d4d2ece60e6d21a5325e5707e7941a89736857628ccd2fd282ab` |

C PAD: `_CODE` 4800..4CE3, `game_main` 4AD0. Ambos entram pelo header em 406F.
RGBDS 1.0.3 / GBDK 4.5.0. Host ROM SHA256:
`9fb1e6e4a637796b8624bd2de6c9abaa9e758546b620cb5dc8441b07c288bc63`.
Linux mGBA commit `358230c82773aec67dff2995eb77fbd84f8ea8a2`, lib SHA256
`ee5795ed0eee7e0c4bd724dd73c490011d74e50af7b7bc1fe48b1079f033a29e`.

Evidências temporárias desta sessão, mantidas fora do Git:

- C PAD offline: `/tmp/netdeget-pad-natural-SMiyR7/run.log`.
- Reação offline após correção visual: `/tmp/maker-natural-zwv7hotm/run.log`.
- Testador portátil C PAD: `/tmp/maker-natural-e_ot118_/run.log`.
  Estado 01=GO, A fixou resultado 21 hexadecimal; B reiniciou e A antecipado
  produziu estado 03. Após retorno, o jogo abriu novamente com estado 00.

## Repita o teste offline

Prepare uma ROM própria e uma fixture SRAM/flash **sintética** com o jogo G001
no primeiro bloco e slot BOX2. O testador verifica o formato e usa cópias em
um novo diretório temporário. Não aponte para saves reais.

```sh
python3 tools/validation/offline.py c-pad "$ROM" "$MGBA_SOURCE" "$MGBA_BUILD" \
  "$SYNTHETIC_BOX2_SAVE" "$SYNTHETIC_FLASH"
# Troque c-pad por pad-test ou c-reaction.
```

O driver usa somente joypad durante a execução; as leituras de memória servem
para verificar estado. A montagem da flash ocorre antes do boot. O teste
confere retorno, reabertura, flash inalterada e hash da ROM. Não testa download.
A macro é específica desta fixture/menu e não é um controlador universal.

## Repita a aquisição natural

O checkout mGBA mantém `tools/mbc6/run_netdeget_local.py`. Use uma fixture SRAM
com catálogo vazio, flash apagada descartável e o REON local com catálogo
baseline de quatro entradas mais G001. Não use credenciais pessoais.

```sh
python3 "$MGBA_SOURCE/tools/mbc6/run_netdeget_local.py" "$ROM" "$MGBA_BUILD" \
  "$EMPTY_SYNTHETIC_SAVE" "$ERASED_SYNTHETIC_FLASH" build/c-pad/game.flash \
  --payload-sha256 ab49fffb02e1b918d442a876508ed83c75ffc32fbbfa482cb8a3b9e46d70381c \
  --body-sha256 f46337ae8627482742511c5d508aaa0ac66930de93c9fe2814fd0c00a02324ba \
  --catalog-sha256 d5323f206466632a447ceb68168175af5d8c6de66e441c9a58f7868c65e679e6
```

Essas opções foram publicadas no commit mGBA
`280b62ffc2c5add122ddee843ec19d07d9174ad0`; confira `--help` no checkout usado. A macro e os asserts de oito contadores cobrem PAD, não o jogo
de reação. Novas variantes exigem expectativas próprias, não apenas novos
hashes. O runner cria DNS local8053 e usa REON8088; encerre os fixtures ao terminar.

### Rodada C PAD via HTTP

CONFIRMED: aquisição natural GET+POST, catálogo de 437 bytes e wrapper de
1114 bytes exatos; escolha BOX2 e escrita do payload inteiro; controles oito
bits, release, Start+Select, BOX1 item16 e nova entrada com contadores zerados.
Em core novo: entrada, A, release, saída e flash inalterada. O restante da
flash, hidden/protection e ROM permaneceram iguais aos baselines.

Evidência do chat mGBA: `/tmp/mgba-netdeget-local-e964hi6b/run.log` e
`/tmp/mgba-netdeget-local-e964hi6b/reopened/run.log`. REON usou fixture local
isolada; nenhum dado de produção foi necessário.

### Rodada C PAD em produção REON

CONFIRMED em 2026-10-06: o chat mGBA executou o mesmo C PAD contra o
REON de produção, usando DNS real na porta 53 e sockets normais, sem servidor
loopback. A aquisição pelo host original, armazenamento de 8192 bytes, oito
controles e releases, saída, reabertura com estado zerado e execução em core
novo passaram. O restante da flash ficou igual ao baseline e a abertura em
core novo não alterou a flash. O runtime testado continua sendo 358230c82;
os hashes do payload e wrapper nesta página permanecem iguais.

Evidências mantidas fora do Git:
`/tmp/mgba-netdeget-production-zqeg16la/run.log`,
`/tmp/mgba-netdeget-production-zqeg16la/reopened/run.log` e
`/tmp/mgba-netdeget-production-zqeg16la/c-pad-controls.png`. O responsável
REON corroborou as requisições de catálogo e corpo e implantou G001 como
conteúdo gratuito opt-in, com a atribuição MIT. Contas e credenciais sintéticas
da rodada não são publicadas neste repositório.

Esta evidência de produção cobre C PAD; o jogo de reação continua validado
somente offline. Não amplia a cobertura para hardware ou runtime padrão GBDK.
