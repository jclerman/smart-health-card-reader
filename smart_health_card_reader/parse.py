"""Parsing functions for Smart Health Cards encrypted as QR codes."""
import base64
import json
import zlib
from typing import List, Set


def qr_int_str_to_b64(qr_int_str: str) -> str:
    """Take the numeric part of the data decoded from the Smart Health Card QR code.

    A Smart Health Card QR code encodes a URL, which starts with 'shc:/'.
    The remaining text is a numeric string (string composed only of numerals).
    That numeric string can be decoded by this function.
    """
    # check that only numerals appear
    found_chars: Set[str] = set(qr_int_str)
    invalid_chars: Set[str] = found_chars - set("0123456789")
    if len(invalid_chars) > 0:
        raise ValueError(f"Invalid characters found (non-numeric): {invalid_chars}")

    str_len: int = len(qr_int_str)
    if str_len % 2 > 0:
        raise ValueError(f"Odd number of characters ({str_len}) in input - invalid!")

    decoded_chars: List[str] = []
    for start in range(0, str_len, 2):
        char: str = chr(int(qr_int_str[start : start + 2]) + 45)
        decoded_chars.append(char)
    return "".join(decoded_chars)


def b64_to_fields(b64: str) -> List[str]:
    """Convert the SHC-QR-code single base64 string to the 3 fields it contains."""
    raws: List[str] = b64.split(".")
    header = b64_decode(raws[0]).decode("utf-8")
    payload = zlib.decompress(b64_decode(raws[1]), -15).decode("utf-8")
    signature = raws[2]
    return [header, payload, signature]


def b64_decode(b64: str) -> bytes:
    """Decode Smart Health Card base64-encoded data to corresponding string."""
    decoded: bytes = base64.b64decode(b64 + "==", altchars=b"-_", validate=True)
    return decoded


if __name__ == "__main__":
    while True:
        arg = input("Please enter something: ")
        b64 = qr_int_str_to_b64(arg)
        fields = b64_to_fields(b64)
        print(f"JWS Header: {fields[0]}")  # noqa: T001
        print(f"JWS Payload: {fields[1]}")  # noqa: T001
        print(json.dumps(json.loads(fields[1]), indent=4, sort_keys=True))  # noqa: T001
        print(f"JWS Signature: {fields[2]}")  # noqa: T001
