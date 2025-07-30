"""
metadata.py
This file is part of py-bmdope.
py-bmdope is a Python package for Block Metadata-Driven Order-Preserving Encryption (BMDOPE).
It provides functionalities for managing metadata related to encryption and decryption processes.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

BLOCK_SIZE = 16

def encrypt_metadata(byte_array: list[int], key: bytes, iv: bytes) -> bytes:
    """
    Encrypts metadata using AES-128 in CBC mode with custom padding.
    This function takes a list of byte values, concatenates them, and applies
    a custom padding scheme. The padding consists of a `0xFF` byte followed by
    N bytes, where N is the number of bytes needed to reach a multiple of the
    block size, and each of the N bytes has the value of N. The padded data is
    then encrypted using AES-128 in CBC mode. Finally, the resulting
    ciphertext is reversed before being returned.
    
    Args:
        byte_array (list[int]): A list of integers representing the metadata
            bytes. Each integer must be between 0 and 255.
        key (bytes): The 16-byte AES encryption key.
        iv (bytes): The 16-byte initialization vector for CBC mode.
    Returns:
        bytes: The reversed, encrypted metadata as a bytes object.
    
    Raises:
        ValueError: If the key or IV is not 16 bytes long, or if `byte_array`
            is not a list of integers or contains values outside the 0-255
            range.
    """
    global BLOCK_SIZE
    
    if not isinstance(key, bytes) or len(key) != 16:
        raise ValueError("Key must be exactly 16 bytes long.")
    if not isinstance(byte_array, list) or not all(isinstance(b, int) for b in byte_array):
        raise ValueError("Byte array must be a list of integers.")
    if not all(0 <= b < 256 for b in byte_array):
        raise ValueError("Invalid byte value in byte array. Must be between 0 and 255.")
    if not isinstance(iv, bytes) or len(iv) != 16:
        raise ValueError("IV must be exactly 16 bytes long.")
    
    concatenated = b''.join(bytes([b]) for b in byte_array)
    padding_length = (BLOCK_SIZE - (len(concatenated) + 1) % BLOCK_SIZE) % BLOCK_SIZE
    concatenated += b'\xFF' + bytes([padding_length] * padding_length)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(concatenated) + encryptor.finalize()

    return ciphertext[::-1]

def decrypt_metadata(encrypted_bytes: bytes, key: bytes, iv: bytes) -> list[int]:
    """
    Decrypts metadata using AES in CBC mode.
    This function takes a byte string, a 16-byte key, and a 16-byte IV
    to perform decryption. It first reverses the input `encrypted_bytes`
    before proceeding with AES-CBC decryption. The decryption process
    stops when a special end-of-file marker (b'\\xFF') is encountered
    in the decrypted data. The final output is truncated at this marker
    and returned as a list of integers.
    
    Args:
        encrypted_bytes (bytes): The encrypted data to be decrypted.
        key (bytes): The 16-byte AES encryption key.
        iv (bytes): The 16-byte initialization vector for CBC mode.
    
    Raises:
        ValueError: If the key or IV is not 16 bytes long, or if
                    `encrypted_bytes` is not a bytes object.
    
    Returns:
        list[int]: A list of integers representing the decrypted bytes,
                   with padding and the EOF marker removed.
    """
    if not isinstance(key, bytes) or len(key) != 16:
        raise ValueError("Key must be exactly 16 bytes long.")
    if not isinstance(encrypted_bytes, bytes):
        raise ValueError("Encrypted bytes must be a bytes object.")
    if not isinstance(iv, bytes) or len(iv) != 16:
        raise ValueError("IV must be exactly 16 bytes long.")
    
    ciphertext = encrypted_bytes[::-1]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_output = b''
    
    # Collect blocks from back to front
    blocks = [ciphertext[i:i + BLOCK_SIZE] for i in range(0, len(ciphertext), BLOCK_SIZE)]

    # CBC decryption: we need previous blocks to XOR
    for i in range(len(blocks)):
        curr_block = blocks[i]

        decrypted = decryptor.update(curr_block)
        decrypted_output += decrypted

        if b'\xFF' in decrypted:
            break
    
    eof_index = decrypted_output.find(b'\xFF')
    if eof_index != -1:
        decrypted_output = decrypted_output[:eof_index]
    
    return [b for b in decrypted_output]