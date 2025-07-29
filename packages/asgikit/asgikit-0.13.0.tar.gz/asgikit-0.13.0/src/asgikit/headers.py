import copy
from collections.abc import Iterable

from asgikit._constants import HEADER_ENCODING


class Headers:
    __slots__ = ("_data",)

    def __init__(self, data: Iterable[tuple[bytes, bytes]] | dict[str, str]):
        self._data = {}

        if not data:
            return

        if isinstance(data, dict):
            self._data = {
                key: value if isinstance(value, list) else [value]
                for key, value in data.items()
            }

            return

        for key, value in data:
            decoded_key = key.decode(HEADER_ENCODING).lower()
            decoded_value = value.decode(HEADER_ENCODING)

            if decoded_key not in self._data:
                self._data[decoded_key] = []

            self._data[decoded_key].append(decoded_value)

    def get(self, key: str, default: str = None) -> str | None:
        if values := self._data.get(key.lower()):
            return values[0]
        return default

    def get_all(self, key: str) -> list[str]:
        return self._data.get(key.lower(), [])

    def encode(self) -> Iterable[tuple[bytes, bytes]]:
        for name, value in self._data.items():
            encoded_name = name.encode(HEADER_ENCODING)
            encoded_value = ", ".join(value).encode(HEADER_ENCODING)
            yield encoded_name, encoded_value

    def __getitem__(self, key: str) -> str:
        if value := self._data.get(key):
            return value[0]
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self) -> Iterable[str]:
        return iter(self._data)

    def __copy__(self):
        headers = Headers([])
        headers._data = copy.copy(self._data)
        return headers

    def __deepcopy__(self, memo):
        headers = Headers([])
        headers._data = copy.deepcopy(self._data, memo=memo)
        return headers

    def __eq__(self, other):
        if isinstance(other, Headers):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other

        return False

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)


class MutableHeaders(Headers):
    def __init__(self):
        super().__init__([])

    def add(self, key: str, value: str):
        key_lower = key.lower()
        if key_lower not in self._data:
            self._data[key_lower] = [value]
        else:
            self._data[key_lower].append(value)

    def set(self, key: str, value: str | list[str]):
        key_lower = key.lower()
        if isinstance(value, list):
            self._data[key_lower] = value
        else:
            self._data[key_lower] = [value]

    def __setitem__(self, key: str, value: str | list[str]):
        self.set(key, value)

    def __delitem__(self, key: str):
        del self._data[key.lower()]
