from asgikit.multi_value_dict import MultiValueDict, MutableMultiValueDict


def test_initial_data():
    data = [("a", 1), ("b", 2)]
    d = MultiValueDict(data)
    assert d == {"a": [1], "b": [2]}


def test_add_single_value():
    d = MutableMultiValueDict()

    d.add("a", 1)
    assert d == {"a": [1]}

    d.add("a", 2)
    assert d == {"a": [1, 2]}


def test_set_single_value():
    d = MutableMultiValueDict()

    d.set("a", 1)
    assert d == {"a": [1]}

    d.set("a", 2)
    assert d == {"a": [2]}


def test_add_list():
    d = MutableMultiValueDict()

    d.add("a", [1, 2])
    assert d == {"a": [1, 2]}

    d.add("a", [3, 4])
    assert d == {"a": [1, 2, 3, 4]}


def test_set_list():
    d = MutableMultiValueDict()

    d.set("a", [1, 2])
    assert d == {"a": [1, 2]}

    d.set("a", [3, 4])
    assert d == {"a": [3, 4]}


def test_setitem_single_value():
    d = MutableMultiValueDict()

    d["a"] = 1
    assert d == {"a": [1]}

    d["a"] = 2
    assert d == {"a": [2]}


def test_setitem_list():
    d = MutableMultiValueDict()

    d["a"] = [1, 2]
    assert d == {"a": [1, 2]}

    d["a"] = [3, 4]
    assert d == {"a": [3, 4]}


def test_get_first():
    d = MutableMultiValueDict()
    d["a"] = [1, 2]
    assert d.get_first("a") == 1


def test_get_all():
    d = MutableMultiValueDict()
    d["a"] = [1, 2]
    assert d.get("a") == [1, 2]


def test_getitem():
    d = MutableMultiValueDict()
    d["a"] = [1, 2]
    assert d["a"] == [1, 2]
