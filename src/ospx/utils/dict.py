import re
from collections import OrderedDict
from typing import MutableMapping, Union


def find_key(dict: MutableMapping, pattern: str) -> str:
    """Finds the first key name in dict that matches the given pattern
    """
    try:
        return [k for k in dict.keys() if re.search(pattern, k)][0]
    except Exception:
        return 'ELEMENTNOTFOUND'


def find_type_identifier_in_keys(dict: MutableMapping) -> str:
    """Finds the first key name in dict that contains one of the following type identifier strings:
    [Unknown|Real|Integer|String|Boolean]
    """
    key_list = ['Unknown', 'Real', 'Integer', 'String', 'Boolean']
    type_identifier = []
    for key in dict:
        key_without_index = re.sub(r'^\d{6}_', '', key)

        if key_without_index in key_list:
            type_identifier.append(key_without_index)

    return type_identifier[0] if type_identifier else 'ELEMENTNOTFOUND'


def shrink_dict(dict: MutableMapping, unique_keys: Union[list[str], None] = None) -> dict:
    """Identifies doubled entries in the passed in dict and returns a new dict with doubled entries removed.
    """
    unique_keys = unique_keys or []
    unique_keys_string: str = "['" + "']['".join(unique_keys) + "']"
    # sort an ordered dict for attribute (child) where the dict is to make unique for
    eval_string = f'sorted(dict.items(), key=lambda x: x[1]{unique_keys_string})'

    # list doubles and remember for deleting
    seen = set([])
    remove_key = []

    for key in OrderedDict(eval(eval_string)):
        proove_value = eval(f'value{unique_keys}')
        if proove_value in seen:
            remove_key.append(key)
        else:
            seen.add(eval(f'value{unique_keys}'))

    return {key: dict[key] for key in dict.keys() if key not in remove_key}
