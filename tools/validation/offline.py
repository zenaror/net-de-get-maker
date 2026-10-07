#!/usr/bin/env python3
"""Fixture-only launch/control/exit checks. Never writes the source ROM or saves."""
import argparse
import ctypes
import os
import hashlib
import json
import shlex
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
flags_path = a.mgba_build / 'CMakeFiles/mgba.dir/flags.make'
flags_text = flags_path.read_text()
flags_line = flags_text.split('C_DEFINES = ')[1].splitlines()[0]
defines = [value.replace('\\"', '"') for value in shlex.split(flags_line)]
library = a.mgba_build / 'libmgba.so'
assert library.exists(), 'requires the matching build library'
loaded = ctypes.CDLL(str(library.resolve()))
expected_version = ctypes.c_char_p.in_dll(loaded, 'projectVersion').value.decode()
expected_commit = ctypes.c_char_p.in_dll(loaded, 'gitCommit').value.decode()
runtime_env = dict(os.environ)
for key in ('LD_LIBRARY_PATH', 'LD_PRELOAD'):
    runtime_env.pop(key, None)
subprocess.run(['cc', '-O2', *defines,
               '-I'+str(a.mgba_source/'include'), '-I'+str(a.mgba_build/'include'),
               '-I'+str(a.mgba_source/'src/third-party/libmobile'),
               '-I'+str(a.mgba_build/'libmobile'),
               str(Path(__file__).with_name('natural.c')), str(library),
               '-Wl,-rpath,'+str(a.mgba_build), '-o', str(root/'runner')], check=True)
macro = ['0:900','8:3','0:180','1:3','0:360','1:3','0:60','1:3',
         '0:240','16:3','0:90','1:3','0:60','1:3','0:180']
checks = {}
def append_stage(*pairs):
    macro.extend(pairs)
    return len(macro) - 1
if a.example == 'c-reaction':
    checks['initial_go'] = 14
    checks['reset'] = append_stage('2:3','0:20')
    checks['early'] = append_stage('1:3','0:20')
    checks['go'] = append_stage('2:3','0:120')
    checks['result'] = append_stage('1:3','0:20')
    checks['reset_again'] = append_stage('2:3','0:20')
else:
    for key in [1,2,8,4,16,32,64,128]:
        checks['inputs'] = append_stage(f'{key}:3','0:20')
checks['hold_exit'] = append_stage('12:3')
checks['partial_release'] = append_stage('4:3')
checks['exit'] = append_stage('0:300')
checks['reentry'] = append_stage('16:3','0:90','1:3','0:60','1:3','0:20')
with (root/'run.log').open('w') as out:
    subprocess.run([str(root/'runner'),str(a.rom),str(root),*macro],stdout=out,
                   stderr=subprocess.STDOUT,check=True,env=runtime_env)
log = (root/'run.log').read_text()
assert log.splitlines()[0] == f'version={expected_version} commit={expected_commit}', 'loaded runtime identity mismatch'
stages = {int(l.split()[0].split('=')[1]): l for l in (root/'run.log').read_text().splitlines() if l.startswith('stage=')}
def counters(stage):
    return bytes.fromhex(stages[stage].split('counters=')[1].split()[0])
if a.example == 'c-reaction':
    for name, state in [('initial_go',1),('reset',0),('early',3),('go',1),('result',2),('reset_again',0)]:
        assert counters(checks[name])[1] == state, name
    assert counters(checks['reset_again'])[0] == 0, 'reaction reset score'
    assert counters(checks['result'])[:2] == counters(checks['result']-1)[:2], 'result must freeze'
else:
    assert counters(checks['inputs']) == bytes([1]*8), 'eight input counters'
    assert 'held=00' in stages[checks['inputs']], 'input release'
for name in ['hold_exit', 'partial_release']:
    assert 'A=0 ' in stages[checks[name]] and 'IME=0 ' in stages[checks[name]], name
assert 'A=20 ' in stages[checks['exit']] and 'pc=517E ' in stages[checks['exit']], 'host return'
assert 'SP=FFF6 ' in stages[checks['exit']], 'host stack'
assert 'A=0 ' in stages[checks['reentry']], 'BOX2 relaunch'
assert counters(checks['reentry'])[:2] == bytes(2), 'state reset'
if a.example != 'c-reaction':
    assert counters(checks['reentry']) == bytes(8), 'input state reset'
assert (root/'padtest.sav.flash').read_bytes() == f, 'game changed flash'
assert (root/'padtest.sav').read_bytes()[0x4F2:0x5F2] == s[0x4F2:0x5F2], 'Index/Box records changed'
assert digest(a.rom.read_bytes()) == rom_sha, 'source ROM changed'
(root/'report.json').write_text(json.dumps({'example':a.example, 'passed':True,
    'fixture_staged_before_boot':True, 'natural_download_tested':False,
    'library_sha256':digest(library.read_bytes()), 'project_version':expected_version, 'git_commit':expected_commit, 'payload_sha256':digest(payload),
    'macro':macro, 'check_stages':checks, 'flash_unchanged':True,
    'index_box_records_unchanged':True}, indent=2))
print('PASS:', a.example, root)
