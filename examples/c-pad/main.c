/* A deliberately small GBDK compiler integration; no cartridge crt or libraries. */
typedef unsigned char u8;
#define REG(a) (*(volatile u8 *)(a))
volatile __at(0xD800) u8 frame;
volatile __at(0xD801) u8 pressed;
volatile __at(0xD802) u8 held;
volatile __at(0xD803) u8 counts[8];
#include "font.h"

/* APIJoypad has a register ABI; preserve the SDCC callee-saved BC explicitly. */
static void joypad(void) __naked {
    __asm
    push bc
    call #0x027c
    pop bc
    ret
    __endasm;
}
static void wait_frame(void) {
    while (REG(0xFF44) >= 144) {}
    while (REG(0xFF44) < 144) {}
}
static void tile(volatile u8 *p, u8 n) {
    while (REG(0xFF41) & 3) {}
    *p = n;
}
static u8 glyph(u8 c) {
    if (c >= 'A' && c <= 'Z') return c - 'A' + 1;
    if (c >= '0' && c <= '9') return c - '0' + 27;
    return 0;
}
static void text(volatile u8 *p, const char *s) {
    while (*s) tile(p++, glyph(*s++));
}
static u8 hex(u8 v) { return v < 10 ? v + 27 : v - 9; }
void game_main(void) {
    unsigned int i;
    u8 n;
#ifndef REACTION
    u8 mask;
    volatile u8 *row;
#endif
    frame = pressed = held = 0;
    for (n = 0; n != 8; ++n) counts[n] = 0;
    /* Turn LCD off only in VBlank; interrupts stay disabled for this example. */
    while (REG(0xFF44) < 144) {}
    REG(0xFF40) = 0; REG(0xFF4F) = 0;
    for (i = 0; i != sizeof(font); ++i) REG(0x8000 + i) = font[i];
    for (i = 0; i != 1024; ++i) REG(0x9800 + i) = 0;
    REG(0xFF4F) = 1;
    for (i = 0; i != 1024; ++i) REG(0x9800 + i) = 0;
    REG(0xFF4F) = 0; REG(0xFF47) = 0xE4;
    REG(0xFF68) = 0x80;
    REG(0xFF69) = 0xFF; REG(0xFF69) = 0x7F;
    REG(0xFF69) = 0xB5; REG(0xFF69) = 0x56;
    REG(0xFF69) = 0x4A; REG(0xFF69) = 0x29;
    REG(0xFF69) = 0; REG(0xFF69) = 0;
    REG(0xFF42) = REG(0xFF43) = 0;
    REG(0xFF40) = 0x91;
    #ifdef REACTION
    text((u8 *)0x9804, "REACTION");
    text((u8 *)0x9821, "WAIT FOR GO");
    text((u8 *)0x9861, "A REACT B RESET");
    text((u8 *)0x98A1, "START SELECT EXIT");
    counts[2] = 90;
#else
    text((u8 *)0x9806, "C PAD TEST");
    text((u8 *)0x9821, "A"); text((u8 *)0x9841, "B");
    text((u8 *)0x9861, "START"); text((u8 *)0x9881, "SELECT");
    text((u8 *)0x98A1, "RIGHT"); text((u8 *)0x98C1, "LEFT");
    text((u8 *)0x98E1, "UP"); text((u8 *)0x9901, "DOWN");
#endif
    for (;;) {
        joypad(); pressed = REG(0xFF97); held = REG(0xFF96); ++frame;
        if ((held & 12) == 12) return;
#ifdef REACTION
        if (pressed & 2) { counts[0] = counts[1] = 0; counts[2] = 90; }
        if (counts[1] == 0) {
            if (pressed & 1) { counts[1] = 3; }
            else if (--counts[2] == 0) counts[1] = 1;
        } else if (counts[1] == 1) {
            if (pressed & 1) counts[1] = 2;
            else if (counts[0] != 255) ++counts[0];
        }
        text((u8 *)0x9821, counts[1] == 0 ? "WAIT FOR GO" :
             counts[1] == 1 ? "GO         " : counts[1] == 2 ? "RESULT     " : "TOO EARLY  ");
        tile((u8 *)0x9841, hex(counts[0] >> 4));
        tile((u8 *)0x9842, hex(counts[0] & 15));
#else
        row = (u8 *)0x9820; mask = 1;
        for (n = 0; n != 8; ++n) {
            if (pressed & mask) ++counts[n];
            text(row + 10, held & mask ? "ON " : "OFF");
            tile(row + 16, hex(counts[n] >> 4));
            tile(row + 17, hex(counts[n] & 15));
            row += 32; mask <<= 1;
        }
        #endif
        wait_frame();
    }
}
