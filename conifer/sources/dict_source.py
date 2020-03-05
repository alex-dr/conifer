from pyrsistent import thaw

from .schema_utils import coerce_value, iter_schema, nest_value
from conifer.utils import get_in, recursive_update


class DictLoader(object):
    """Barebones loader for conf already in a dict-like."""

    def __init__(self, data):
        self._data = data

    def load_config(self, schema):
        """Load configuration values for this schema."""
        partial_config = thaw(self._data)

        for key_name, sub_schema in iter_schema(schema):
            try:
                raw_value = get_in(self._data, key_name)
            except KeyError:
                continue

            coerced_value = coerce_value(raw_value, sub_schema)

            recursive_update(partial_config, nest_value(key_name, coerced_value))

        return partial_config
