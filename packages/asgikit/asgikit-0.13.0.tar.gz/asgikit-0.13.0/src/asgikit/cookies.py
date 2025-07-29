import http.cookies
import itertools
from collections.abc import Iterable
from http.cookies import SimpleCookie

from asgikit._constants import HEADER_ENCODING
from asgikit.multi_value_dict import MultiValueDict


def _parse_cookie(cookie: str):
    for chunk in cookie.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            # Assume an empty name per
            # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            # unquote using Python's algorithm.
            # pylint: disable=protected-access
            yield key, http.cookies._unquote(val)


def parse_cookie(cookies: list[str]) -> MultiValueDict[str]:
    """
    Return a dictionary parsed from a `Cookie:` header string.
    """

    values = itertools.chain.from_iterable(_parse_cookie(cookie) for cookie in cookies)
    return MultiValueDict(values)


def encode_cookies(cookies: SimpleCookie) -> Iterable[tuple[bytes, bytes]]:
    for c in cookies.values():
        yield b"Set-Cookie", c.output(header="").strip().encode(HEADER_ENCODING)
