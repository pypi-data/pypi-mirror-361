import unittest
import os
from pybmdope.metadata import encrypt_metadata, decrypt_metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.key = b"W:]-I~Yzx;?E506h"  # 16-character key
        self.byte_array = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90]
        self.iv = os.urandom(16)
        self.encrypted_data = encrypt_metadata(self.byte_array, self.key, self.iv)

    def test_encrypt_metadata(self):
        self.assertIsInstance(self.encrypted_data, bytes)
        self.assertGreater(len(self.encrypted_data), 0)

    def test_decrypt_metadata(self):
        encrypted_bytes = os.urandom(32) + self.encrypted_data  # Simulating a longer encrypted byte string
        decrypted_data = decrypt_metadata(encrypted_bytes, self.key, self.iv)
        self.assertEqual(decrypted_data, self.byte_array)

    # def test_invalid_key_length(self):
    #     with self.assertRaises(ValueError):
    #         encrypt_metadata(self.byte_array, "short_key")
    #     with self.assertRaises(ValueError):
    #         decrypt_metadata(self.encrypted_data, "short_key")

if __name__ == "__main__":
    unittest.main()
