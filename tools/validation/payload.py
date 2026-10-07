#!/usr/bin/env python3
"""Offline checks for full-block extraction and game-ID checksums; no database."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.payload import extract_image, finalize_payload, set_game_id

class PayloadTests(unittest.TestCase):
    def payload(self, blocks=1):
        data = bytearray(blocks * 8192)
        data[5] = blocks
        data[9:13] = b'G000'
        data[-1] = 0xA5
        return data

    def test_full_declared_blocks_and_last_byte(self):
        for blocks in (1, 2, 16):
            data = self.payload(blocks)
            result = extract_image(bytes(0x4000) + data)
            self.assertEqual(len(result), blocks * 8192)
            self.assertEqual(result[-1], 0xA5)

    def test_zero_padding_is_preserved(self):
        data = self.payload()
        data[-1] = 0
        self.assertEqual(len(finalize_payload(data)), 8192)
        self.assertEqual(finalize_payload(data)[-1], 0)

    def test_assigned_id_recomputes_checksum(self):
        for game_id in ('G000', 'G002', 'G999'):
            result = set_game_id(self.payload(), game_id)
            self.assertEqual(result[9:13], game_id.encode())
            expected = (sum(result) - sum(result[0x6D:0x6F])) & 0xFFFF
            self.assertEqual(int.from_bytes(result[0x6D:0x6F], 'little'), expected)
            self.assertEqual(finalize_payload(result), result)

    def test_reject_invalid_id(self):
        for game_id in ('G1000', 'G１２３', 'X123', ''):
            with self.assertRaises(ValueError):
                set_game_id(self.payload(), game_id)

    def test_reject_missing_or_inconsistent_blocks(self):
        for payload in (b'', self.payload()[:-1], self.payload() + b'\0'):
            with self.assertRaises(ValueError):
                finalize_payload(payload)
        for count in (0, 17):
            data = self.payload()
            data[5] = count
            with self.assertRaises(ValueError):
                finalize_payload(data)

if __name__ == '__main__':
    unittest.main()
