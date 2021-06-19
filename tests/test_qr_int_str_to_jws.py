import pytest
from smart_health_card_reader.parse import qr_int_str_to_jws as qis2jws


@pytest.mark.parametrize(
    "in_val,out_val",
    [
        ("43", "X"),
        ("4343", "XX"),
    ]
)
def test_qis2jws_convert(in_val: str, out_val: str):
    assert qis2jws(in_val) == out_val