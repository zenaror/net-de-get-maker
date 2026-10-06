; Original Net de Get input diagnostic homebrew payload.
SECTION "Input tester payload", ROMX[$4000], BANK[1]

    jp InputTesterStart
    dw InputTesterStart - $4000     ; host entry offset (SDK header contract)
    db 1                           ; one 8 KiB flash block
    db 1, 6, 1                    ; category / genre / unknown
    db "G001"
    dw 0
    db "PAD TEST", 0
    ds $4024 - @, $00
    db "Visible input tester", 0
    ds $4044 - @, $00
    db $FF
    ds $406F - @, $00

InputTesterStart:
    ldh a, [$FF41]                 ; preserve host STAT and interrupt enable
    ld b, a
    ldh a, [$FFFF]
    ld c, a
    push bc
    di                             ; keep host VBlank text callbacks off-screen
    xor a
    ld [wInputTesterFrame], a
    ld [wInputTesterPressedMask], a
    ld [wInputTesterHeldMask], a
    ld hl, wInputTesterCounters
    ld b, 8
.clearCounters
    ld [hli], a
    dec b
    jr nz, .clearCounters

    call InitDisplay
    call DrawStatic
    call DrawDynamic

.mainLoop
    call $027C                     ; APIJoypad
    ldh a, [$FF97]                 ; newly pressed bits
    ld [wInputTesterPressedMask], a
    ld [wInputTesterPressScratch], a
    ldh a, [$FF96]                 ; currently held bits
    ld [wInputTesterHeldMask], a
    ld a, [wInputTesterFrame]
    inc a
    ld [wInputTesterFrame], a

    ld a, [wInputTesterPressScratch]
    ld hl, wInputTesterCounters
    ld b, 8
.countBits
    srl a
    jr nc, .nextBit
    inc [hl]
.nextBit
    inc hl
    dec b
    jr nz, .countBits
    ld a, [wInputTesterHeldMask]
    and $0C                        ; Start + Select together
    cp $0C
    jp z, ExitInputTester
    call DrawDynamic
    call WaitNextFrame
    jr .mainLoop

ExitInputTester:
    di
    ld a, $10                      ; Maker: backed out of game
    ld [$C671], a
    ld de, 0
    call $0150                     ; APISetVBlank
    call $0153                     ; APISetTimer
    call $0156                     ; APISetLCDC
    call $0159                     ; APISetSerial
    xor a
    ldh [$FF42], a
    ldh [$FF43], a
    ldh [$FF4F], a
    pop bc
    ld a, c
    ldh [$FFFF], a
    ld a, b
    ldh [$FF41], a
    ei
    ret

InitDisplay:
    xor a
    ldh [$FF40], a                 ; LCD off while replacing graphics
    ldh [$FF4F], a                 ; VRAM bank 0

    ld hl, $8000
    ld de, FontTiles
    ld bc, FontTilesEnd - FontTiles
.copyFont
    ld a, [de]
    inc de
    ld [hli], a
    dec bc
    ld a, b
    or c
    jr nz, .copyFont

    ld hl, $9800
    ld bc, $0400
    ld d, 0
.clearTileMap
    ld a, d
    ld [hli], a
    dec bc
    ld a, b
    or c
    jr nz, .clearTileMap

    ld a, 1
    ldh [$FF4F], a                 ; clear CGB tile attributes too
    ld hl, $9800
    ld bc, $0400
    ld d, 0
.clearAttributes
    ld a, d
    ld [hli], a
    dec bc
    ld a, b
    or c
    jr nz, .clearAttributes
    xor a
    ldh [$FF4F], a

    ld a, $E4
    ldh [$FF47], a                 ; DMG-compatible grayscale mapping
    ld a, $80
    ldh [$FF68], a                 ; BG palette 0, auto-increment
    ld hl, BgPalette
    ld b, 8
.writePalette
    ld a, [hli]
    ldh [$FF69], a
    dec b
    jr nz, .writePalette

    xor a
    ldh [$FF42], a                 ; SCY
    ldh [$FF43], a                 ; SCX
    ld a, $91
    ldh [$FF40], a                 ; LCD on, BG on, unsigned tile data, map $9800
    ret

DrawStatic:
    ld hl, TextTitle
    ld b, 6
    ld c, 0
    call DrawAscii
    ld hl, LabelA
    ld b, 1
    ld c, 1
    call DrawAscii
    ld hl, LabelB
    ld b, 1
    ld c, 2
    call DrawAscii
    ld hl, LabelStart
    ld b, 1
    ld c, 3
    call DrawAscii
    ld hl, LabelSelect
    ld b, 1
    ld c, 4
    call DrawAscii
    ld hl, LabelRight
    ld b, 1
    ld c, 5
    call DrawAscii
    ld hl, LabelLeft
    ld b, 1
    ld c, 6
    call DrawAscii
    ld hl, LabelUp
    ld b, 1
    ld c, 7
    call DrawAscii
    ld hl, LabelDown
    ld b, 1
    ld c, 8
    jp DrawAscii

DrawDynamic:
    xor a
    ld [wInputTesterBitIndex], a
    ld a, 1
    ld [wInputTesterBitMask], a
.drawRows
    ld a, [wInputTesterBitIndex]
    inc a
    ld [wInputTesterDrawY], a
    ld a, [wInputTesterHeldMask]
    ld b, a
    ld a, [wInputTesterBitMask]
    and b
    jr z, .drawOff
    ld hl, TextOn
    jr .drawState
.drawOff
    ld hl, TextOff
.drawState
    ld a, [wInputTesterDrawY]
    ld c, a
    ld b, 10
    call DrawAscii

    ld a, [wInputTesterBitIndex]
    ld e, a
    ld d, 0
    ld hl, wInputTesterCounters
    add hl, de
    ld a, [hl]
    call FormatHexByte
    ld hl, wInputTesterHexText
    ld a, [wInputTesterDrawY]
    ld c, a
    ld b, 16
    call DrawAscii

    ld a, [wInputTesterBitIndex]
    inc a
    ld [wInputTesterBitIndex], a
    ld a, [wInputTesterBitMask]
    rlca
    ld [wInputTesterBitMask], a
    ld a, [wInputTesterBitIndex]
    cp 8
    jr nz, .drawRows
    ret

; Draw an ASCII string at tile column B, row C. The fixture uses an
; independent tile font so the host's banked Maker text renderer is untouched.
DrawAscii:
    ld a, b
    ld [wInputTesterDrawX], a
    ld a, c
    ld [wInputTesterDrawY], a
.drawChar
    ld a, [hli]
    and a
    ret z
    call AsciiToTile
    ld [wInputTesterDrawTile], a
    push hl

    ld a, [wInputTesterDrawY]
    ld l, a
    ld h, 0
    add hl, hl
    add hl, hl
    add hl, hl
    add hl, hl
    add hl, hl                  ; row * 32
    ld a, [wInputTesterDrawX]
    ld e, a
    ld d, 0
    add hl, de
    ld de, $9800
    add hl, de
    call WaitHBlank
    ld a, [wInputTesterDrawTile]
    ld [hl], a

    ld a, [wInputTesterDrawX]
    inc a
    ld [wInputTesterDrawX], a
    pop hl
    jr .drawChar

AsciiToTile:
    cp $41
    jr c, .digit
    cp $5B
    jr nc, .digit
    sub $40
    ret
.digit
    cp $30
    jr c, .space
    cp $3A
    jr nc, .space
    sub $30
    add 27
    ret
.space
    xor a
    ret

WaitHBlank:
    ldh a, [$FF41]
    and 3
    jr nz, WaitHBlank
    ret

WaitNextFrame:
    ldh a, [$FF44]
    cp 144
    jr nc, .leaveVBlank
.waitVBlank
    ldh a, [$FF44]
    cp 144
    jr c, .waitVBlank
    ret
.leaveVBlank
    ldh a, [$FF44]
    cp 144
    jr nc, .leaveVBlank
    jr .waitVBlank

FormatHexByte:
    ld b, a
    swap a
    and $0F
    call .hexDigit
    ld [wInputTesterHexText], a
    ld a, b
    and $0F
    call .hexDigit
    ld [wInputTesterHexText+1], a
    xor a
    ld [wInputTesterHexText+2], a
    ret
.hexDigit
    cp 10
    jr c, .digit
    add $37
    ret
.digit
    add $30
    ret

BgPalette:
    db $FF, $7F                   ; white
    db $B5, $56                   ; light gray
    db $4A, $29                   ; dark gray
    db $00, $00                   ; black

TextTitle:
    db "PAD TEST", 0
LabelA:
    db "A", 0
LabelB:
    db "B", 0
LabelStart:
    db "START", 0
LabelSelect:
    db "SELECT", 0
LabelRight:
    db "RIGHT", 0
LabelLeft:
    db "LEFT", 0
LabelUp:
    db "UP", 0
LabelDown:
    db "DOWN", 0
TextOn:
    db "ON ", 0
TextOff:
    db "OFF", 0

INCLUDE "pad_font.inc"

; C700 is host-persistent working state (post-game ROM reads C705).
; Use the Maker minigame workspace instead.
SECTION "Input tester state", WRAMX[$D800], BANK[1]
wInputTesterFrame:        ds 1
wInputTesterPressedMask:  ds 1
wInputTesterHeldMask:     ds 1
wInputTesterCounters:     ds 8
wInputTesterPressScratch: ds 1
wInputTesterBitIndex:     ds 1
wInputTesterBitMask:      ds 1
wInputTesterDrawY:        ds 1
wInputTesterHexText:      ds 3
wInputTesterDrawX:        ds 1
wInputTesterDrawTile:     ds 1
