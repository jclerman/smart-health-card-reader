"""Unit-tests for parsing functions."""
import json

import pytest

from smart_health_card_reader.parse import (
    b64_decode,
    b64_to_fields,
    extract_jws_data_from_qr_data,
    get_public_key_url,
    get_public_keyset_json,
)
from smart_health_card_reader.parse import qr_int_str_to_b64 as qis2jws
from smart_health_card_reader.parse import validate_jws_data

from .conftest import TEST_B64_SIG, TEST_FULL_B64


def test_qr_int_str_to_b64(qr_int_str):
    """Test that qr_int_str_to_b64() correctly decodes a full SHC QR-encoded digit-string into base64 string."""
    assert qis2jws(qr_int_str) == TEST_FULL_B64


def test_get_sig():
    """Test correct signature extraction from the base64 string encoding of a complete SMART Health Card."""
    assert b64_to_fields(TEST_FULL_B64)[2] == TEST_B64_SIG
    assert len(b64_decode(TEST_B64_SIG)) == 64


@pytest.mark.parametrize(
    "in_val,out_val",
    [
        ("43", "X"),
        ("4343", "XX"),
    ],
)
def test_qis2jws_convert(in_val: str, out_val: str):
    """Confirm that qr_int_str_to_b64 converts numeric strings to bas64-encoded strings as expected."""
    assert qis2jws(in_val) == out_val


@pytest.mark.parametrize("in_val", ["abc", "123#", "A123", "--12", "123 "])
def test_qis2jws_reject_invalid_chars(in_val: str):
    """Confirm that qr_int_str_to_b64 rejects non-numeric input strings."""
    with pytest.raises(ValueError):
        qis2jws(in_val)


def test_get_public_key_url(test_jws_payload):
    """Confirm that the public-key URL is correctly extracted from a JWS payload by get_public_key_url."""
    pk_url = get_public_key_url(test_jws_payload)
    assert (
        pk_url == "https://spec.smarthealth.cards/examples/issuer/.well-known/jwks.json"
    )


def test_get_pk(pk_url):
    """Confirm that a public-key is correctly retrieved by get_public_key_json(), given a public-key URL."""
    pk_json: str = get_public_keyset_json(pk_url)
    pk_dict = json.loads(pk_json)
    assert isinstance(pk_dict, dict)
    assert "keys" in pk_dict
    key1 = pk_dict["keys"][0]
    assert key1["kid"] == "3Kfdg-XwP-7gXyywtUfUADwBumDOPKMQx-iELL11W9s"


def test_validate_jws_data(qr_int_str):
    """Test signing validation of JWS data, comparing the internal payload to the internal signature."""
    signed_doc, header, payload, sig = extract_jws_data_from_qr_data(qr_int_str)
    assert validate_jws_data(signed_doc, header, payload, sig)
