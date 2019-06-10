from collections import Mapping


def recursive_update(original, updates):
    """Utility function to update original dictionary recursively.

    Lists are replaced, not updated. New values are added.
    """
    if updates is None:
        return

    for key, value in updates.items():
        if isinstance(value, Mapping):
            # if original has a mapping, recursively update it
            # otherwise, just replace the value with the new mapping
            if key in original and isinstance(original[key], Mapping):
                recursive_update(original[key], value)
            else:
                original[key] = value
        else:
            original[key] = value


def get_in(dic, key):
    """Get maybe-nested value key from dic."""
    # Allow string or list keys
    if isinstance(key, str):
        return dic[key]

    if len(key) == 1:
        return dic[key[0]]
    else:
        return get_in(dic[key[0]], key[1:])


def set_in(dic, key, value):
    """Set maybe nested value for key in dic."""
    # Allow string or list keys
    if isinstance(key, str):
        dic[key] = value
    else:
        if len(key) == 1:
            dic[key[0]] = value
        else:
            if key[0] not in dic:
                dic[key[0]] = {}
            set_in(dic[key[0]], key[1:], value)
