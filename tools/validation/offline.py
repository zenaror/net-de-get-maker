#!/usr/bin/env python3
"""Fixture-only launch/control/exit checks. Never writes the source ROM or saves."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('example', choices=['pad-test', 'c-pad', 'c-reaction'])
p.add_argument('rom', type=Path)
p.add_argument('mgba_source', type=Path)
p.add_argument('mgba_build', type=Path)
p.add_argument('synthetic_box2_save', type=Path)
p.add_argument('synthetic_flash', type=Path)
a = p.parse_args()
repo = Path(__file__).resolve().parents[2]
digest = lambda data: hashlib.sha256(data).hexdigest()
rom_sha = '9fb1e6e4a637796b8624bd2de6c9abaa9e758546b620cb5dc8441b07c288bc63'
assert digest(a.rom.read_bytes()) == rom_sha, 'unexpected host ROM'
s = a.synthetic_box2_save.read_bytes()
f = bytearray(a.synthetic_flash.read_bytes())
assert len(s) == 32768 and s[0x4F2:0x4F4] == b'\x10\x01', 'requires synthetic BOX2 slot fixture'
assert len(f) == 0x100101, 'unexpected flash sidecar layout'
payload = (repo / 'build' / a.example / 'game.flash').read_bytes()
assert len(payload) == 8192
f[:8192] = payload
root = Path(tempfile.mkdtemp(prefix='maker-natural-'))
(root / 'padtest.sav').write_bytes(s)
(root / 'padtest.sav.flash').write_bytes(f)
subprocess.run(['cc', '-O2', '-DENABLE_VFS', '-DENABLE_DIRECTORIES', '-DENABLE_INPUT',
               '-I'+str(a.mgba_source/'include'), '-I'+str(a.mgba_build/'include'),
               str(Path(__file__).with_name('natural.c')), '-L'+str(a.mgba_build),
               '-Wl,-rpath,'+str(a.mgba_build), '-lmgba', '-o', str(root/'runner')], check=True)
macro = ['0:900','8:3','0:180','1:3','0:360','1:3','0:60','1:3',
         '0:240','16:3','0:90','1:3','0:60','1:3']
if a.example == 'c-reaction':
    macro += ['0:140','1:3','0:20','2:3','0:1','1:3','0:20']
    exit_stage, reentry_stage = 22, 58
else:
    macro += ['0:120']
    for key in [1,2,8,4,16,32,64,128]: macro += [f'{key}:3','0:20']
    exit_stage, reentry_stage = 32, 68
macro += ['12:3','0:300'] + ['128:3','0:10']*16 + ['1:3','0:60','1:3','0:20']
with (root/'run.log').open('w') as out:
    subprocess.run([str(root/'runner'),str(a.rom),str(root),*macro],stdout=out,
                   stderr=subprocess.STDOUT,check=True)
stages = {int(l.split()[0].split('=')[1]): l for l in (root/'run.log').read_text().splitlines() if l.startswith('stage=')}
if a.example == 'c-reaction':
    assert stages[16].split('counters=')[1][2:4] == '02', 'reaction result'
    assert stages[20].split('counters=')[1][2:4] == '03', 'early press'
else:
    assert 'counters=0101010101010101' in stages[30] and 'held=00' in stages[30]
assert 'A=20 B=0' in stages[exit_stage], 'host menu after return'
assert 'A=0 B=0' in stages[reentry_stage], 'relaunch'
assert stages[reentry_stage].split('counters=')[1][:4] == '0000', 'state reset'
if a.example != 'c-reaction': assert 'counters=0000000000000000' in stages[reentry_stage]
assert (root/'padtest.sav.flash').read_bytes() == f, 'game changed flash'
assert (root/'padtest.sav').read_bytes()[0x4F2:0x4F4] == b'\x10\x00'
assert digest(a.rom.read_bytes()) == rom_sha, 'source ROM changed'
print('PASS:', a.example, root)
