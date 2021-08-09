"""Unit-test qr_int_str_to_b64."""
import json

import pytest

from smart_health_card_reader.parse import get_public_key_json, get_public_key_url
from smart_health_card_reader.parse import qr_int_str_to_b64 as qis2jws


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
    pk_json: str = get_public_key_json(pk_url)
    pk_dict = json.loads(pk_json)
    assert "keys" in pk_dict
    key1 = pk_dict["keys"][0]
    assert key1["kid"] == "3Kfdg-XwP-7gXyywtUfUADwBumDOPKMQx-iELL11W9s"
