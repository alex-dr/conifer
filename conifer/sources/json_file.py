import json
import os

from .schema_utils import coerce_value, iter_schema, nest_value
from conifer.utils import get_in, recursive_update


class JSONFileLoader(object):
    """Loader for JSON files."""

    def __init__(self, path=None, fp=None):
        """JSON file config loader.

        Must be instantiated with one of path or fp.

        Parameters
        ----------
        path : string
            Path to a json file
        fp : File pointer
            Pointer to an open file object
        """
        if path is not None and fp is not None:
            raise ValueError(
                "JSONFileLoader must be instantiated with one of path or fp"
            )
        if path is None and fp is None:
            raise ValueError(
                "JSONFileLoader must be instantiated with one of path or fp"
            )

        if path is not None:
            path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
        self._path = path
        self._fp = fp

        self._load_data()

    def _load_data(self):
        if self._path is not None:
            if not os.path.exists(self._path):
                self._data = {}
                return
            with open(self._path, "rb") as _fp:
                self._data = json.load(_fp)
        else:
            self._data = json.load(self._fp)

    def load_config(self, schema):
        """Load configuration values for this schema."""
        partial_config = {}

        for key_name, sub_schema in iter_schema(schema):
            try:
                raw_value = get_in(self._data, key_name)
            except KeyError:
                continue
            coerced_value = coerce_value(raw_value, sub_schema)

            recursive_update(partial_config, nest_value(key_name, coerced_value))

        return partial_config
