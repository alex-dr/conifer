from .base_loader import BaseLoader, LoaderMode
from .schema_utils import coerce_value, iter_schema, nest_value
from conifer.utils import recursive_update

import os


class EnvironmentConfigLoader(BaseLoader):
    """Loader for environment variables."""

    mode = LoaderMode.RO

    def __init__(self, prefix=""):
        self._prefix = prefix

    def _load_config(self, schema):
        """Load configuration values for this schema."""
        partial_config = {}

        for key_name, sub_schema in iter_schema(schema):
            environment_key = self._prefix + "_".join(key_name)
            raw_value = os.environ.get(environment_key)
            coerced_value = coerce_value(raw_value, sub_schema)

            if coerced_value is not None:
                recursive_update(partial_config, nest_value(key_name, coerced_value))

        return partial_config
