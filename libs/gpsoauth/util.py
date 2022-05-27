"""Utility functions."""
import binascii


def bytes_to_int(bytes_seq: bytes) -> int:
    """Convert bytes to int."""
    return int.from_bytes(bytes_seq, "big")


def int_to_bytes(num: int, pad_multiple: int = 1) -> bytes:
    """Packs the num into a byte string 0 padded to a multiple of pad_multiple
    bytes in size. 0 means no padding whatsoever, so that packing 0 result
    in an empty string. The resulting byte string is the big-endian two's
    complement representation of the passed in long."""

    # source: http://stackoverflow.com/a/14527004/1231454

    if num == 0:
        return b"\0" * pad_multiple
    if num < 0:
        raise ValueError("Can only convert non-negative numbers.")
    value = hex(num)[2:]
    value = value.rstrip("L")
    if len(value) & 1:
        value = "0" + value
    result = binascii.unhexlify(value)
    if pad_multiple not in [0, 1]:
        filled_so_far = len(result) % pad_multiple
        if filled_so_far != 0:
            result = b"\0" * (pad_multiple - filled_so_far) + result
    return result
