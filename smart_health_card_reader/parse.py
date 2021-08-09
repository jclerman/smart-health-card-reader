"""Parsing functions for Smart Health Cards encrypted as QR codes."""
import base64
import json
import urllib.request
import zlib
from typing import List, Set, Tuple

import cv2

# TODO: Catch 'ImportError: Unable to find zbar shared library' and return user-friendly instructions.
from pyzbar.pyzbar import ZBarSymbol, decode


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix from text.

    If the prefix wasn't found, return the original text; otherwise, return the text without the prefix.
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def png_to_qr_data(png_fn: str) -> str:
    """Extract QR code data from a PNG file containing a single QR code.

    Args:
        png_fn: Path of a PNG file containing a single QR code.

    Returns:
        Data found in the QR code, as a string, minus the 'shc:/' prefix, if it was there.
    """
    image = cv2.imread(png_fn)
    detected_barcodes: List = decode(image, symbols=[ZBarSymbol.QRCODE])
    if len(detected_barcodes) > 1:
        raise Exception("Too many barcodes found - send an image with just one.")
    if len(detected_barcodes) < 1:
        raise Exception("No barcodes found - send an image with one.")
    barcode = detected_barcodes[0]
    print(f"Found a barcode of type {barcode.type}")  # noqa: T001
    raw_data = barcode.data
    return remove_prefix(raw_data.decode("UTF-8"), "shc:/")


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


def b64_to_fields(b64: str) -> Tuple[str, str, str]:
    """Convert the SHC-QR-code single base64 string to the 3 fields it contains.

    Returns:
        3-part Tuple of strings: JSON Web Signature (JWS) Header, JWS Payload, JWS Signature.
    """
    raws: List[str] = b64.split(".")
    header = b64_decode(raws[0]).decode("utf-8")
    payload = zlib.decompress(b64_decode(raws[1]), -15).decode("utf-8")
    signature = raws[2]
    return header, payload, signature


def b64_decode(b64: str) -> bytes:
    """Decode Smart Health Card base64-encoded data to corresponding string."""
    decoded: bytes = base64.b64decode(b64 + "==", altchars=b"-_", validate=True)
    return decoded


def get_public_key_url(payload_json_str: str) -> str:
    """From the JWS Payload, return the public key URL."""
    payload_json = json.loads(payload_json_str)
    issuer_orig_url = payload_json["iss"]
    return f"{issuer_orig_url}/.well-known/jwks.json"


def get_public_key_json(pk_url: str) -> str:
    """Return the public keys as a JSON string, using the public key URL."""
    with urllib.request.urlopen(pk_url) as f:
        pk = f.read().decode("utf-8")
    return pk


if __name__ == "__main__":
    while True:
        arg = input("Please enter something: ")
        b64 = qr_int_str_to_b64(arg)
        fields = b64_to_fields(b64)
        print(f"JWS Header: {fields[0]}")  # noqa: T001
        print(f"JWS Payload: {fields[1]}")  # noqa: T001
        print(json.dumps(json.loads(fields[1]), indent=4, sort_keys=True))  # noqa: T001
        print(f"JWS Signature: {fields[2]}")  # noqa: T001
