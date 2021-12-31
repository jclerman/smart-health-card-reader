"""Parsing functions for Smart Health Cards encrypted as QR codes."""
import base64
import json
import urllib.request
import zlib
from typing import Any, Dict, List, Set, Tuple, Union

import cv2
from fastecdsa import ecdsa
from fastecdsa.point import Point

# TODO: Catch 'ImportError: Unable to find zbar shared library' and return user-friendly instructions.
from pyzbar.pyzbar import ZBarSymbol, decode


def remove_prefix(text: str, prefix: str = "shc:/") -> str:
    """Remove prefix from text.

    If the prefix wasn't found, return the original text; otherwise, return the text without the prefix.
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def img_to_qr_data(png_fn: str) -> str:
    """Extract QR code data from a CV2-supported image file containing a single QR code.

    Supported formats include PNG, JPG, TIF, BMP, and others.

    Args:
        png_fn: Path of an image-file containing a single QR code.

    Returns:
        Data found in the QR code, as a string, minus the 'shc:/' prefix, if it was there.
    """
    image = cv2.imread(png_fn)
    detected_barcodes: List = decode(image, symbols=[ZBarSymbol.QRCODE])
    if len(detected_barcodes) > 1:
        raise Exception(f"Too many barcodes found in {png_fn} - send an image with just one.")
    if len(detected_barcodes) < 1:
        raise Exception(f"No barcodes found in {png_fn} - send an image with one.")
    barcode = detected_barcodes[0]
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


def decode_sig(b64_sig: str) -> Tuple[bytes, bytes]:
    """Decode the base64-encoded signature into the R and S components, as big-endian-byte-encoded integers.

    Returns:
        Tuple[bytes, bytes], where each of the two tuple members are 32 bytes long.
    """
    sig = b64_decode(b64_sig)
    r = sig[0:32]
    s = sig[32:64]
    return r, s


def get_public_key_url(payload_json_str: str) -> str:
    """From the JWS Payload, return the public key URL."""
    payload_json = json.loads(payload_json_str)
    issuer_orig_url = payload_json["iss"]
    return f"{issuer_orig_url}/.well-known/jwks.json"


def get_public_keyset_json(pk_url: str) -> str:
    """Return the public keys as a JSON string, using the public key URL."""
    with urllib.request.urlopen(pk_url) as f:
        pk = f.read().decode("utf-8")
    return pk


def get_public_key_from_keyset(pk_json_str: str, kid: str) -> Dict[str, Union[str, List[str]]]:
    """From public-key-set JSON from a SMART Health protocol-compliant issuer, return key matching a key-ID."""
    pk_dict: Dict[str, List[Dict]] = json.loads(pk_json_str)
    assert "keys" in pk_dict
    pk: Dict[str, Any]
    for pk in pk_dict["keys"]:
        pk_kid = pk["kid"]
        if pk_kid == kid:
            if pk["kty"] != "EC":
                continue
            if pk["use"] != "sig":
                continue
            if pk["alg"] != "ES256":
                continue
            if pk["crv"] != "P-256":
                continue
            if "d" in pk:
                continue
            return pk
    raise KeyError(f"No public key with specified key-ID '{kid}' found.")


def extract_jws_data_from_qr_data(qr_data: str) -> Tuple[str, str, str, str]:
    """From the numeric-digit string directly encoded in a SMART Health QR code, extract JWS data.

    Parameters:
        qr_data: The string directly encoded by a SMART Health QR code.

    Returns:
        Tuple of four strings:
            (1) the signed document (to be validated in a later step).
                This includes the base-64 encoded JWS header & payload.
            (2) the JWS header, as a JSON string
            (3) the JWS payload, as a JSON string
            (4) the JWS signature, base-64 encoded
    """
    qr_data_digit_str: str = remove_prefix(qr_data)  # not always necessary, should always be safe
    b64 = qr_int_str_to_b64(qr_data_digit_str)
    header, payload, sig = b64_to_fields(b64)
    signed_doc = ".".join(b64.split(".")[0:2])
    return signed_doc, header, payload, sig


def validate_jws_data(signed_doc: str, header_json: str, payload_json: str, sig: str) -> bool:
    """Validate JWS data by comparing the encryption signature to the signed content.

    Parameters:
        signed_doc: the signed document, to be validated. This includes the base-64 encoded JWS header & payload.
        header_json: the JWS header, already decoded into a JSON string
        payload_json: the JWS payload, already decoded into a JSON string
        sig: the JWS signature, base-64 encoded

    Returns:
          boolean value - True if the signature matches the content; False otherwise.
    """
    header_dict: Dict[str, str] = json.loads(header_json)
    kid: str = header_dict["kid"]
    pk_url: str = get_public_key_url(payload_json)
    public_keyset_json = get_public_keyset_json(pk_url)
    pk: Dict[str, Union[str, List[str]]] = get_public_key_from_keyset(public_keyset_json, kid)
    assert isinstance(pk["x"], str)
    assert isinstance(pk["y"], str)
    pk_x = int.from_bytes(b64_decode(pk["x"]), byteorder="big")
    pk_y = int.from_bytes(b64_decode(pk["y"]), byteorder="big")
    r, s = decode_sig(sig)
    r_int = int.from_bytes(r, byteorder="big")
    s_int = int.from_bytes(s, byteorder="big")
    return ecdsa.verify((r_int, s_int), signed_doc, Point(pk_x, pk_y))


if __name__ == "__main__":
    while True:
        arg = input("Please enter something: ")
        _, jws_header, jws_payload, jws_sig = extract_jws_data_from_qr_data(arg)
        print(f"JWS Header: {jws_header}")  # noqa: T001
        print(f"JWS Payload: {jws_payload}")  # noqa: T001
        print(json.dumps(json.loads(jws_payload), indent=4, sort_keys=True))  # noqa: T001
        print(f"JWS Signature: {jws_sig}")  # noqa: T001
