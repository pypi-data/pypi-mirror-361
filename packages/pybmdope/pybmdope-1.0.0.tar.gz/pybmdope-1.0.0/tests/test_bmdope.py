import unittest
from pybmdope.bmdope import BMDOPE

class TestBMDOPE(unittest.TestCase):
    def setUp(self):
        self.key = b"W:]-I~Yzx;?E506h"  # 16-character key
        self.bmdope = BMDOPE(self.key)
        
    def test_encrypt_block(self):
        block = b"test"
        key = b"1234567890abcdef"
        encrypted = self.bmdope.encrypt_block(block, key)
        self.assertIsInstance(encrypted, bytes)
        self.assertNotEqual(encrypted, block)

    def test_encrypt_block_invalid_key(self):
        block = b"test"
        key = b"short_key"
        with self.assertRaises(ValueError):
            self.bmdope.encrypt_block(block, key)

    def test_encrypt_block_invalid_block_size(self):
        block = b"toolongblock"
        key = b"1234567890abcdef"
        with self.assertRaises(ValueError):
            self.bmdope.encrypt_block(block, key)

    def test_decrypt_block(self):
        block = b"test"
        key = b"1234567890abcdef"
        encrypted = self.bmdope.encrypt_block(block, key)
        decrypted = self.bmdope.decrypt_block(encrypted, key)
        self.assertEqual(decrypted, block)

    def test_decrypt_block_invalid_key(self):
        encrypted = b"110010101011"
        key = b"short_key"
        with self.assertRaises(ValueError):
            self.bmdope.decrypt_block(encrypted, key)

    def test_plaintext_equals_decrypt(self):
        """Tests if the decrypted data matches the original plaintext."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)

        # Ensure decrypted data matches original plaintext
        self.assertEqual(decrypted1, data1)
        self.assertEqual(decrypted2, data2)
        self.assertEqual(decrypted3, data3)

    def test_order_preserving_property_with_bytes(self):
        """Tests if the lexicographical order of byte strings is preserved using encrypt method."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        # Pre-condition: data1 < data2 < data3
        self.assertTrue(data1 < data2 < data3)

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        # Post-condition: encrypted(data1) < encrypted(data2) < encrypted(data3)
        self.assertTrue(encrypted1 < encrypted2 < encrypted3)

    def test_order_preserving_property_with_numbers(self):
        """Tests if the order of numbers (converted to bytes) is preserved using encrypt method."""
        num1 = (100).to_bytes(8, 'big')
        num2 = (2000).to_bytes(8, 'big')
        num3 = (30000).to_bytes(8, 'big')

        # Pre-condition: num1 < num2 < num3
        self.assertTrue(num1 < num2 < num3)

        encrypted1 = self.bmdope.encrypt(num1)
        encrypted2 = self.bmdope.encrypt(num2)
        encrypted3 = self.bmdope.encrypt(num3)

        # Post-condition: encrypted(num1) < encrypted(num2) < encrypted(num3)
        self.assertTrue(encrypted1 < encrypted2 < encrypted3)

    def test_decrypt_order_preserving_property_with_bytes(self):
        """Tests if the lexicographical order of byte strings is preserved after decryption."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)

        # Post-condition: decrypted(data1) < decrypted(data2) < decrypted(data3)
        self.assertTrue(decrypted1 < decrypted2 < decrypted3)
        self.assertEqual(decrypted1, data1)
        self.assertEqual(decrypted2, data2)
        self.assertEqual(decrypted3, data3)

    def test_decrypt_order_preserving_property_with_numbers(self):
        """Tests if the order of numbers (converted to bytes) is preserved after decryption."""
        num1 = (100).to_bytes(8, 'big')
        num2 = (2000).to_bytes(8, 'big')
        num3 = (30000).to_bytes(8, 'big')

        encrypted1 = self.bmdope.encrypt(num1)
        encrypted2 = self.bmdope.encrypt(num2)
        encrypted3 = self.bmdope.encrypt(num3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)
        
        # Pad the decrypted values to ensure they are comparable
        decrypted1 = decrypted1.rjust(8, b'\x00')
        decrypted2 = decrypted2.rjust(8, b'\x00')
        decrypted3 = decrypted3.rjust(8, b'\x00')

        # Post-condition: decrypted(num1) < decrypted(num2) < decrypted(num3)
        self.assertEqual(decrypted1, num1)
        self.assertEqual(decrypted2, num2)
        self.assertEqual(decrypted3, num3)
        self.assertTrue(decrypted1 < decrypted2 < decrypted3)

if __name__ == "__main__":
    unittest.main()
