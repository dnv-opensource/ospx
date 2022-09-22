import re
from collections import OrderedDict
from typing import List, MutableMapping, Union


def find_key(dict: MutableMapping, pattern: str) -> Union[str, None]:
    """Finds the first key in dict that matches the given pattern
    """
    try:
        return [k for k in dict.keys() if re.search(pattern, k)][0]
    except Exception:
        return None


def find_keys(dict: MutableMapping, pattern: str) -> Union[List[str], None]:
    """Finds all keys in dict that match the given pattern
    """
    try:
        return [k for k in dict.keys() if re.search(pattern, k)]
    except Exception:
        return None


def find_type_identifier_in_keys(dict: MutableMapping) -> Union[str, None]:
    """Finds the first key name in dict that contains one of the following type identifier strings:
    [Integer|Real|Boolean|Enumeration|String|Unknown]
    """
    key_list = ['Integer', 'Real', 'Boolean', 'Enumeration', 'String', 'Unkown']
    type_identifier = []
    for key in dict:
        key_without_index = re.sub(r'^\d{6}_', '', key)

        if key_without_index in key_list:
            type_identifier.append(key_without_index)

    return type_identifier[0] if type_identifier else None


def shrink_dict(dict: MutableMapping, unique_key: Union[list[str], None] = None) -> dict:
    """Identifies doubled entries in the passed in dict and returns a new dict with doubled entries removed.
    """
    unique_key = unique_key or []
    unique_keys_string: str = "['" + "']['".join(unique_key) + "']"
    # sort an ordered dict for attribute (child) where the dict is to make unique for
    eval_string = f'sorted(dict.items(), key=lambda x: x[1]{unique_keys_string})'

    # list doubles and remember for deleting
    seen = set([])
    remove_key = []

    for key, value in OrderedDict(eval(eval_string)).items():  # value is necessary here as it is used in the eval statements below. Do not delete it.
        proove_value = eval(f'value{unique_keys_string}')
        if proove_value in seen:
            remove_key.append(key)
        else:
            seen.add(eval(f'value{unique_keys_string}'))

    return {key: dict[key] for key in dict.keys() if key not in remove_key}
