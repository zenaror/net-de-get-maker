; Host entry and return bridge. Never resets the host stack pointer.
SECTION "C payload", ROMX[$4000], BANK[1]
    jp Entry
    dw Entry - $4000
    db 1, 1, 6, 1
    db "G001"
    dw 0
IF DEF(REACTION)
    db "REACTION", 0
ELSE
    db "C PAD TEST", 0
ENDC
    ds $4024 - @, 0
IF DEF(REACTION)
    db "A react B reset", 0
ELSE
    db "GBDK compiler example", 0
ENDC
    ds $4044 - @, 0
    db $FF
    ds $406F - @, 0
Entry:
    ldh a, [$FF41]
    ld b, a
    ldh a, [$FFFF]
    ld c, a
    push bc
    di
    ldh a, [$FF70]
    push af
    ld a, 1
    ldh [$FF70], a
    call C_ENTRY
    di
.waitExitRelease
    ; Held Select at host entry triggers catalog reconstruction. Return only
    ; after both exit buttons are released; preserve the host stack/IE/STAT.
    call $027C
    ldh a, [$FF96]
    and $0C
    jr nz, .waitExitRelease
    ld a, $10
    ld [$C671], a
    ld de, 0
    call $0150
    call $0153
    call $0156
    call $0159
    xor a
    ldh [$FF42], a
    ldh [$FF43], a
    ldh [$FF4F], a
    pop af
    ldh [$FF70], a
    pop bc
    ld a, c
    ldh [$FFFF], a
    ld a, b
    ldh [$FF41], a
    ei
    ret
    ASSERT @ < $4800
    ds $4800 - @, 0
    INCBIN "c-code.bin"
    ASSERT @ <= $6000
    ds $6000 - @, 0
