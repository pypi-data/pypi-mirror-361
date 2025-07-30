import unittest
from pybmdope.key import reshuffle, split_key, rotate_left, rotate_right

class TestKeyModule(unittest.TestCase):
    def test_reshuffle(self):
        input_str = b"abcdefgh12345678"
        result = reshuffle(input_str)
        self.assertEqual(len(result), 16)
        self.assertNotEqual(result, input_str)

    def test_reshuffle_invalid_length(self):
        with self.assertRaises(ValueError):
            reshuffle("short")

    def test_reshuffle_invalid_type(self):
        with self.assertRaises(ValueError):
            reshuffle(12345)  # Non-bytes input
        with self.assertRaises(ValueError):
            reshuffle(["a", "b", "c"])  # Non-bytes input

    def test_split_key(self):
        key = b"abcdefgh12345678"
        parts, shifts = split_key(key)
        self.assertEqual(len(parts), 4)
        self.assertEqual(len(shifts), 4)
        self.assertEqual(parts[0], b"abcd")
        self.assertEqual(parts[1], b"efgh")
        self.assertEqual(parts[2], b"1234")
        self.assertEqual(parts[3], bytes([b1 ^ b2 ^ b3 for b1, b2, b3 in zip(parts[0], parts[1], parts[2])]))
        self.assertEqual(shifts, b"5678")

    def test_split_key_invalid_length(self):
        with self.assertRaises(ValueError):
            split_key("short")

    def test_split_key_invalid_type(self):
        with self.assertRaises(ValueError):
            split_key(12345)  # Non-bytes input
        with self.assertRaises(ValueError):
            split_key(["a", "b", "c"])  # Non-bytes input

    def test_rotate_left(self):
        self.assertEqual(rotate_left(0b10101010, 3), 0b01010101)
        self.assertEqual(rotate_left(0b11110000, 4), 0b00001111)

    def test_rotate_right(self):
        self.assertEqual(rotate_right(0b10101010, 3), 0b01010101)
        self.assertEqual(rotate_right(0b11110000, 4), 0b00001111)

if __name__ == "__main__":
    unittest.main()
