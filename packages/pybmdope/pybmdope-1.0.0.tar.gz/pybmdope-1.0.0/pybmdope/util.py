def binary_to_bytes(binary_data: bytes) -> bytes:
    """
    Converts a byte string of binary digits ('0' and '1') to a raw bytes object.

    The input binary string is padded with leading zeros to ensure its length is a
    multiple of 8 before being converted into a sequence of bytes.

    Args:
        binary_data (bytes): A bytes object containing a string of binary digits
            (e.g., b'110101').

    Returns:
        bytes: The raw bytes representation of the input binary string.
    """
    bit_str = binary_data.decode()
    padded_bit_str = bit_str.zfill((len(bit_str) + 7) // 8 * 8)
    bit_int = int(padded_bit_str, 2)
    byte_len = len(padded_bit_str) // 8
    return bit_int.to_bytes(byte_len, 'big')

def bytes_to_binary(byte_data: bytes) -> bytes:
    """
    Converts a bytes object to its binary string representation.

    This function takes a sequence of bytes, converts each byte into its 8-bit
    binary form, joins them into a single string, removes any leading zeros
    from the combined string, and then encodes the final string back into
    a bytes object.

    Args:
        byte_data (bytes): The input bytes object to be converted.

    Returns:
        bytes: The binary string representation of the input, with leading
                zeros stripped, encoded as a bytes object.
    """
    bit_str = ''.join(format(byte, '08b') for byte in byte_data).lstrip('0')
    return bit_str.encode()
