"""Unit-test qr_int_str_to_b64."""
import pytest

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
