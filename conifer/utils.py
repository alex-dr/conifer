from collections import Mapping


def recursive_update(original, updates):
    """Utility function to update original dictionary recursively.

    Lists are replaced, not updated. New values are added.
    """
    for key, value in updates.iteritems():
        if isinstance(value, Mapping):
            # if original has a mapping, recursively update it
            # otherwise, just replace the value with the new mapping
            if key in original and isinstance(original[key], Mapping):
                recursive_update(original[key], value)
            else:
                original[key] = value
        else:
            original[key] = value
