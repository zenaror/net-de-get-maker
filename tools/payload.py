"""Offline full-block payload/checksum helpers shared by Maker workflows."""
BLOCK_BYTES = 8192

def finalize_payload(payload):
    data = bytearray(payload)
    if len(data) < 0x6F or not 1 <= data[5] <= 16:
        raise ValueError('expected a header declaring 1..16 flash blocks')
    if len(data) != data[5] * BLOCK_BYTES:
        raise ValueError('payload length must match its declared flash blocks')
    checksum = (sum(data) - sum(data[0x6D:0x6F])) & 0xFFFF
    data[0x6D:0x6F] = checksum.to_bytes(2, 'little')
    return bytes(data)

def set_game_id(payload, game_id):
    if len(game_id) != 4 or game_id[0] != 'G' or not game_id[1:].isascii() or not game_id[1:].isdigit():
        raise ValueError('expected game ID Gddd')
    data = bytearray(payload)
    if len(data) < 13:
        raise ValueError('missing game header')
    data[9:13] = game_id.encode('ascii')
    return finalize_payload(data)

def extract_image(image):
    if len(image) <= 0x4005:
        raise ValueError('missing linked image header at $4000')
    blocks = image[0x4005]
    if not 1 <= blocks <= 16:
        raise ValueError('expected 1..16 flash blocks')
    return finalize_payload(image[0x4000:0x4000 + blocks * BLOCK_BYTES])
