#!/usr/bin/env python3
"""Create an exact padded flash payload and Maker mode-5 HTTP body, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bmvj_compress import bmvj_compress

def package(image, stem):
    data = bytearray(image[0x4000:0x6000])
    if len(data) != 8192 or any(image[:0x4000]) or any(image[0x6000:]):
        raise ValueError('example must occupy only $4000-$5FFF in a zero-filled RGBDS image')
    if data[0] != 0xC3 or data[5] != 1 or not 0x406F <= int.from_bytes(data[1:3], 'little') < 0x6000:
        raise ValueError('invalid one-block example header')
    if int.from_bytes(data[3:5], 'little') != int.from_bytes(data[1:3], 'little') - 0x4000:
        raise ValueError('entry offset and jump disagree')
    if 0 not in data[15:36] or 0 not in data[36:68] or data[68] != 255:
        raise ValueError('title/description must terminate inside their header fields; title marker must be FF')
    game_id = bytes(data[9:13]).decode('ascii')
    if len(game_id) != 4 or game_id[0] != 'G' or not game_id[1:].isdigit():
        raise ValueError('expected ID Gddd')
    checksum = (sum(data) - sum(data[0x6D:0x6F])) & 65535
    data[0x6D:0x6F] = checksum.to_bytes(2, 'little')
    stem.parent.mkdir(parents=True, exist_ok=True)
    payload = bytes(data)
    body = bmvj_compress(payload)
    payload_path = stem.with_suffix('.flash')
    body_path = stem.parent / ('0000.' + game_id + '.cgb')
    payload_path.write_bytes(payload)
    body_path.write_bytes(body)
    metadata = {'gameId': game_id, 'blocks': 1, 'category': data[6], 'genre': data[7],
                'titleHex': data[15:36].split(b'\0')[0].hex(),
                'descriptionHex': data[36:68].split(b'\0')[0].hex(),
                'downloadFilename': body_path.name, 'price': 0,
                'payloadSha256': hashlib.sha256(payload).hexdigest(),
                'bodySha256': hashlib.sha256(body).hexdigest(), 'checksum': checksum,
                'payloadBytes': len(payload), 'bodyBytes': len(body)}
    stem.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rgbds_image', type=Path)
    p.add_argument('output_stem', type=Path)
    a = p.parse_args()
    package(a.rgbds_image.read_bytes(), a.output_stem)
