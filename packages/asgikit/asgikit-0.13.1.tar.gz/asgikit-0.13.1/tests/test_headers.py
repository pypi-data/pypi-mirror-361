import pytest

from asgikit.headers import Headers


@pytest.mark.parametrize(
    "raw,parsed",
    [
        ([(b"a", b"1"), (b"b", b"2")], {"a": ["1"], "b": ["2"]}),
        ([(b"a", b"1, 2"), (b"b", b"3, 4")], {"a": ["1, 2"], "b": ["3, 4"]}),
        (
            [(b"a", b"1"), (b"a", b"2"), (b"b", b"3"), (b"b", b"4")],
            {"a": ["1", "2"], "b": ["3", "4"]},
        ),
        ([], {}),
    ],
)
def test_parse(raw, parsed):
    result = Headers(raw)
    assert result == parsed


@pytest.mark.parametrize(
    "parsed,encoded",
    [
        ({"a": ["1"], "b": ["2"]}, [(b"a", b"1"), (b"b", b"2")]),
        (
            {"a": ["1", "2"], "b": ["3", "4"]},
            [(b"a", b"1, 2"), (b"b", b"3, 4")],
        ),
        ({}, []),
    ],
)
def test_encode(parsed, encoded):
    headers = Headers(parsed)
    result = list(headers.encode())
    assert result == encoded
