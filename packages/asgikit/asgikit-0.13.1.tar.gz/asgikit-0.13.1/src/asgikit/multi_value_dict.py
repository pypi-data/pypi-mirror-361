import copy
from collections.abc import Iterable
from typing import Generic, TypeVar

__all__ = ("MultiValueDict", "MutableMultiValueDict")

T = TypeVar("T")


class MultiValueDict(Generic[T]):
    __slots__ = ("_data",)

    def __init__(
        self,
        data: Iterable[tuple[str, T]] = None,
    ):
        self._data = {}

        if not data:
            return

        for key, value in data:
            if key not in self._data:
                self._data[key] = []

            self._data[key].append(value)

    def get_first(self, key: str, default: T = None) -> T | None:
        if value := self._data.get(key):
            return value[0]

        return default

    def get(self, key: str, default: list[T] = None) -> list[T] | None:
        return self._data.get(key, default)

    def keys(self) -> Iterable[str]:
        return self._data.keys()

    def values(self) -> Iterable[list[T]]:
        return self._data.values()

    def items(self) -> Iterable[tuple[str, T]]:
        return self._data.items()

    def __getitem__(self, key: str) -> list[T]:
        return self._data[key]

    def __contains__(self, key: str):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self) -> Iterable[str]:
        return self._data.__iter__()

    def __copy__(self):
        return MultiValueDict(copy.copy(self._data))

    def __deepcopy__(self, memo):
        return MultiValueDict(copy.deepcopy(self._data, memo=memo))

    def __eq__(self, other):
        if isinstance(other, MultiValueDict):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other

        return False

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)


class MutableMultiValueDict(MultiValueDict[T]):
    def add(self, key: str, value: T | list[T]):
        if key not in self._data:
            self._data[key] = []

        if isinstance(value, list):
            self._data[key] += value
        else:
            self._data[key].append(value)

    def set(self, key: str, value: T | list[T]):
        if isinstance(value, list):
            self._data[key] = value
        else:
            self._data[key] = [value]

    def __setitem__(self, key: str, value: T | list[T]):
        self.set(key, value)

    def __delitem__(self, key: str):
        del self._data[key]
