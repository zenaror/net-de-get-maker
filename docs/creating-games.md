# Criando um minigame

## 1. Escolha um exemplo

Execute os comandos do README. Comece por `examples/pad-test/main.asm` para
RGBDS ou `examples/c-pad/main.c` para C. `c-reaction` compila o mesmo arquivo C
com `REACTION` definido: espere GO, pressione A e veja o tempo em hexadecimal;
B reinicia. Apertar A antes de GO mostra TOO EARLY. Start+Select volta ao host.
O tempo é contado em iterações sincronizadas com frames, não em milissegundos;
FF significa saturação em 255. Este exemplo não salva recordes.

O build faz tudo localmente. Não execute `make push` para testar: o publisher
legado usa um banco externo e precisa de configuração própria.

## 2. Entenda a entrada e o header

O host carrega a primeira janela do jogo em `$4000-$5FFF` e chama a entrada.
Preserve o retorno e a pilha do host. Nos exemplos, `$4000` contém `JP $406F`;
o word em +3 contém `$006F`. O programa começa depois do header.

| Offset no payload | Conteúdo usado pelos exemplos |
| --- | --- |
| +0 | JP para entrada |
| +3 | entrada menos `$4000`, word little endian |
| +5 | número de blocos de **8 KiB**, aqui 1 |
| +6/+7/+8 | categoria / gênero / campo legado 1 |
| +9..+12 | ID de quatro bytes, aqui G001 |
| +13 | append ID, word; aqui zero |
| +15 | título terminado em zero, limitado até +35 |
| +36 | descrição terminada em zero, limitada até +67 |
| +68 | marcador de título, FF |
| +109/+110 | checksum aditivo little endian |
| +111 | entrada dos exemplos |

O significado de campos desconhecidos não foi confirmado. O Maker legado usa
3B B3 no lugar do checksum: o host tem um caminho que aceita esse marcador.
O novo build calcula o checksum real de todos os bytes declarados, excluindo
somente +109/+110.

O charmap do host em `include/charmap.asm` não é ASCII: espaço é 10 e dígitos
começam em 20. Os exemplos PAD conservam o texto ASCII da fixture validada;
o espaço 20 pode desaparecer nos menus do host. A fonte usada dentro do jogo
é independente. Para títulos novos com o renderer do host, use o charmap e
refaça a validação do catálogo e seus hashes.

## 3. Memória e gráficos

MBC6 tem duas janelas independentes de 8 KiB: A `$4000-$5FFF` e B
`$6000-$7FFF`. O BANK[1] de RGBDS identifica um banco físico de 16 KiB no
arquivo de link; não é um seletor MBC6. Estes exemplos ocupam somente a metade A.

Use WRAM banco 1 em D800..D80A para o estado destes exemplos. O startup C
seleciona banco 1 e restaura SVBK ao sair. C700 contém estado persistente do
host; usá-lo para variáveis do jogo já causou corrupção do retorno ao menu.
O restante da WRAM não foi certificado como livre para qualquer aplicação.

Os exemplos instalam uma fonte própria em VRAM, zeram mapa e atributos,
configuram a paleta CGB e desenham somente quando VRAM está acessível.
O exemplo C desliga LCD em VBlank e liga LCDC=91. Interrupções ficam desabilitadas
durante o jogo; a espera de frame consulta LY. Não use `HALT` nesse modelo.

## 4. Entrada e saída

APIJoypad em 027C atualiza FF96 (held) e FF97 (pressed). Bits:
A=0, B=1, Select=2, Start=3, Right=4, Left=5, Up=6, Down=7.
`pressed` evita contar repetidamente um botão segurado. Leia uma vez por frame.

Ao sair, os exemplos escrevem 10 em C671 (estado legado de saída), limpam os
callbacks 0150/0153/0156/0159 com DE=0, zeram scroll/VBK, restauram IE/STAT e
fazem EI/RET. A ponte C também restaura SVBK. Não use JP para reset do cartucho.
Esse contrato foi validado neste host e com estes exemplos; não é prova de
compatibilidade com todos os jogos ou de hardware real.

## 5. Empacote e prepare o servidor

`tools/package.py` recebe a imagem intermediária RGBDS, extrai a janela A,
preserva o bloco inteiro com padding zero, calcula checksum e chama o compressor
original do Maker. Não trime zeros: o host valida o comprimento declarado;
uma última página parcial pode reter dados anteriores do buffer do instalador.
O build rejeita bytes fora da janela e header/entrada inconsistentes.

O wrapper contém: byte de comprimento do comentário (0), reservado (0), modo
(5), comprimento comprimido (word), comprimento de saída (word), dois bytes
reservados e stream a partir de +9. `bmvj_compress()` já devolve esse corpo
completo; não acrescente outro envelope. Não sirva `.flash` como se fosse `.cgb`.

Para REON local, forneça `0000.G001.cgb` e os campos de `game.json` ao processo de
fixture. O schema de catálogo observado no host tem quatro bytes reservados
antes dos campos usuais; o encoder deve usar o contrato atual do REON. O host
faz GET e depois POST autenticado com corpo vazio no mesmo recurso. Um router
que aceita apenas GET não completa o fluxo natural.

Teste aquisição, escolha do BOX, gravação, abertura, controles, saída,
reabertura no mesmo core e abertura em core novo. Os fixtures atuais mudam o
jogo de BOX2 para BOX1 ao sair; no catálogo sintético ele vira item 16.
A causa dessa mudança não foi estabelecida.

## 6. Acrescente funcionalidades gradualmente

As declarações em `include/api/` documentam a ABI de registradores do Maker.
Muitas foram reconstruídas estaticamente: disponibilidade do símbolo não
certifica sua interação com o jogo. A primeira integração C cobre somente
APIJoypad e a limpeza de callbacks na saída. Áudio, arquivos, skills, callbacks
ativos e banking de múltiplos blocos precisam de exemplos e traces próprios.
