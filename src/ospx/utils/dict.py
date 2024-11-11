import re
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Any


def find_key(dict_in: MutableMapping[Any, Any], pattern: str) -> str | None:
    """Find the first key in dict that matches the given pattern."""
    try:
        return next(key for key in dict_in if re.search(pattern, key))
    except Exception:  # noqa: BLE001
        return None


def find_keys(dict_in: MutableMapping[Any, Any], pattern: str) -> list[str] | None:
    """Find all keys in dict that match the given pattern."""
    try:
        return [k for k in dict_in if re.search(pattern, k)]
    except Exception:  # noqa: BLE001
        return None


def find_type_identifier_in_keys(dict_in: MutableMapping[Any, Any]) -> str | None:
    """Find the first type identifier in dict.

    Find. the first key name in dict that contains one of the following type identifier strings:
    [Integer|Real|Boolean|Enumeration|String|Unknown].
    """
    key_list: list[str] = ["Integer", "Real", "Boolean", "Enumeration", "String", "Unkown"]
    type_identifier: list[str] = []
    for key in dict_in:
        key_without_index = re.sub(r"^\d{6}_", "", key)

        if key_without_index in key_list:
            type_identifier.append(key_without_index)

    return type_identifier[0] if type_identifier else None


def shrink_dict(dict_in: MutableMapping[Any, Any], unique_key: list[str] | None = None) -> dict[Any, Any]:
    """Identify doubled entries in the passed in dict and return a new dict with doubled entries removed."""
    _unique_key: list[str] = unique_key or []
    unique_keys_string: str = "['" + "']['".join(_unique_key) + "']"
    # sort an ordered dict for attribute (child) where the dict is to make unique for
    eval_string: str = f"sorted(dict_in.items(), key=lambda x: str(x[1]{unique_keys_string}))"

    # Identify doublettes and collect them for subsequent removal
    seen: set[Any] = set()
    remove_key: list[Any] = []

    # value is necessary here as it is used in the eval statements below. Do not delete it.
    for key, value in OrderedDict(eval(eval_string)).items():  # noqa: B007, PERF102, S307
        proove_value = eval(f"value{unique_keys_string}")  # noqa: S307
        if proove_value in seen:
            remove_key.append(key)
        else:
            seen.add(eval(f"value{unique_keys_string}"))  # noqa: S307

    return {key: dict_in[key] for key in dict_in if key not in remove_key}
