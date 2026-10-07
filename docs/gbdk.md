# GBDK: integração experimental

## O que já funciona

GBDK-2020 4.5.0 compila C para SM83 dentro de um payload carregado pelo host.
`c-pad` passou por entrada natural, oito botões, saída e reabertura no mesmo
core. `c-reaction` passou por rodada válida, entrada antecipada, reset, saída e
reabertura. Veja a matriz de evidências antes de extrapolar esses resultados.

O port é uma integração inicial do compilador. Não é um port completo do SDK
Maker nem da biblioteca GBDK para Net de Get.

## Exemplo REACTION

O diretório [`examples/c-reaction/`](../examples/c-reaction/) contém `main.c`,
`start.asm` e um README próprios. `make c-reaction` compila essa entrada. Ela
seleciona REACTION e inclui a implementação compartilhada de C PAD; o header
faz o mesmo com a ponte assembly. Os programas e o contrato do host continuam
idênticos aos payloads validados, sem duplicar código de ABI e gráficos.

## Como o build funciona

1. `lcc -no-crt -no-libs` compila sem startup de cartucho e bibliotecas padrão.
2. `_CODE` começa em 4800; o linker produz Intel HEX e mapa largo.
3. `c_extract.py` rejeita código fora de 4800..5FFF e áreas de runtime com tamanho
   não zero. Copia código e constantes para `c-code.bin` e encontra `game_main`.
4. RGBDS monta o header e a ponte em 406F; inclui o código C em 4800.
5. `package.py` cria payload, wrapper e metadata offline.

`-K` dispensa o checker de cartucho do lcc; o extrator aplica os limites próprios
do payload. `link-symbols.s` declara referências para as atribuições padrão
_shadow_OAM/.STACK do linker, sem reservar armazenamento nem executar código.
O programa não usa esses símbolos, OAM do GBDK ou SP=E000.

Globals são explicitamente `__at(D800...)` e inicializados em `game_main`.
Não acrescente globals comuns ou inicializadas sem implementar e validar um
runtime de inicialização: o build rejeita essas áreas. Constantes ficam no
código. Não existe heap, crt0, interrupt vector próprio ou reset de SP.

## ABI e runtime

A release 4.5.0 usa a ABI SM83 padrão `__sdcccall(1)`. Não faça cast de 027C para
um ponteiro C: a API do host recebe/retorna registradores com outro contrato.
A função naked `joypad()` é uma ponte assembly sem argumentos; preserva BC,
chama 027C e retorna. O C lê os resultados em FF96/FF97.

A ponte de entrada preserva IE/STAT e SVBK na pilha do host, faz DI, seleciona
WRAM1, chama C, limpa callbacks e retorna ao dispatcher original. Não há uma
nova pilha. Mantenha poucas chamadas aninhadas: nas amostras naturais do jogo de reação o
SP observado foi FFEE e voltou a FFF6 no menu; isso não estabelece o máximo
consumido nem um orçamento universal. Recursão e grandes arrays locais exigem
outra estratégia de pilha e validação.

Não use automaticamente `printf`, `malloc`, `wait_vbl_done`, `add_VBL`, sprites,
áudio ou funções banked normais do GBDK: elas pressupõem globals/startup e
banking de cartucho próprios. Uma futura ponte para callbacks precisa respeitar
a convenção real do dispatcher do host e preservar registradores; não basta
instalar uma função `__interrupt` que termina com RETI. Isso ainda não foi validado.

O banking usual de 16 KiB do GBDK não modela diretamente as duas janelas MBC6 de
8 KiB. O build atual rejeita código além de um bloco. Uma próxima etapa precisa
implementar wrappers de mapper e far calls, com preservação das duas janelas.

## Toolchain reproduzida

Release oficial Linux x86_64: GBDK 4.5.0.
Arquivo `gbdk-linux64.tar.gz`, SHA256:
`d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c`.
RGBDS 1.0.3 e Python 3. Nenhum binário de toolchain é versionado aqui.

Fontes primárias:

- [Release 4.5.0](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.5.0)
- [Opções da toolchain](https://gbdk.org/docs/api/docs_toolchain_settings.html)
- [Migração e ABI SDCC](https://gbdk.org/docs/api/docs_migrating_versions.html)
- [Guia de uso GBDK](https://gbdk.org/docs/api/docs_using_gbdk.html)
