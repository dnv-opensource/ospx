import pytest

from ospx.utils.dict import shrink_dict


def test_shrink_dict_removes_duplicates_from_nested_unique_key() -> None:
    source = {
        "first": {"_attributes": {"name": "A"}, "value": 1},
        "second": {"_attributes": {"name": "B"}, "value": 2},
        "third": {"_attributes": {"name": "A"}, "value": 999},
    }

    result = shrink_dict(source, unique_key=["_attributes", "name"])

    assert result == {
        "first": {"_attributes": {"name": "A"}, "value": 1},
        "second": {"_attributes": {"name": "B"}, "value": 2},
    }


def test_shrink_dict_keeps_original_order_of_remaining_entries() -> None:
    source = {
        "gamma": {"_attributes": {"name": "C"}},
        "alpha": {"_attributes": {"name": "A"}},
        "beta": {"_attributes": {"name": "B"}},
        "delta": {"_attributes": {"name": "A"}},
    }

    result = shrink_dict(source, unique_key=["_attributes", "name"])

    assert list(result.keys()) == ["gamma", "alpha", "beta"]


def test_shrink_dict_returns_input_when_all_unique() -> None:
    source = {
        "one": {"_attributes": {"name": "A"}},
        "two": {"_attributes": {"name": "B"}},
        "three": {"_attributes": {"name": "C"}},
    }

    result = shrink_dict(source, unique_key=["_attributes", "name"])

    assert result == source


def test_shrink_dict_raises_key_error_if_unique_key_path_missing() -> None:
    source = {
        "one": {"_attributes": {"name": "A"}},
        "two": {"wrong": {"name": "A"}},
    }

    with pytest.raises(KeyError):
        _ = shrink_dict(source, unique_key=["_attributes", "name"])


def test_shrink_dict_is_tolerant_to_dict_values_being_empty_strings() -> None:
    source = {
        "one": {"_attributes": {"name": ""}},
        "two": {"_attributes": {"name": ""}},
    }

    result = shrink_dict(source, unique_key=["_attributes", "name"])

    assert result == {
        "one": {"_attributes": {"name": ""}},
    }


def test_shrink_dict_is_tolerant_to_dict_values_being_none() -> None:
    source = {
        "one": {"_attributes": {"name": None}},
        "two": {"_attributes": {"name": None}},
    }

    result = shrink_dict(source, unique_key=["_attributes", "name"])

    assert result == {
        "one": {"_attributes": {"name": None}},
    }
