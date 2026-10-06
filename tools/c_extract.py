#!/usr/bin/env python3
"""Reject code outside the single MBC6 window or hidden startup/data areas."""
from pathlib import Path
import re
import sys
image = bytearray(0x10000)
seen = set()
base = 0
for line in Path(sys.argv[1]).read_text().splitlines():
    record = bytes.fromhex(line[1:])
    if sum(record) & 255: raise ValueError('bad Intel HEX checksum')
    size, address, kind = record[0], int.from_bytes(record[1:3], 'big'), record[3]
    if kind == 0:
        for i, value in enumerate(record[4:4+size]):
            a = base + address + i
            if not 0x4800 <= a < 0x6000: raise ValueError(f'code outside window: {a:x}')
            image[a] = value; seen.add(a)
    elif kind == 4: base = int.from_bytes(record[4:6], 'big') << 16
    elif kind not in (1,): raise ValueError(f'unsupported HEX record {kind}')
map_text = Path(sys.argv[2]).read_text()
entry = re.search(r'([0-9A-F]{8})\s+_game_main\b', map_text)
if not entry: raise ValueError('game_main not found; use wide linker map')
for area in ('_DATA', '_INITIALIZED', '_INITIALIZER', '_GSINIT', '_GSFINAL', '_HOME', '_HRAM'):
    lengths = re.findall(r'([0-9A-F]{8})\s+l_' + area + r'\b', map_text)
    if any(int(x, 16) for x in lengths): raise ValueError('unexpected runtime area '+area)
end = max(seen) + 1
Path(sys.argv[3]).write_bytes(image[0x4800:end])
print(int(entry[1], 16))
