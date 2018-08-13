# builtin
import json
import os

# third party
from jsonschema import Draft4Validator

# this package
from .sources import EnvironmentConfig


class Conifer(object):
    """Conifer is a object to encapsulate your applications configuration.

    Conifer is instantiated with a schema and configuration sources.

    By default, Conifer will use the built-in EnvironmentConfig source only.
    """

    # The populated configuration data
    _config = None

    def __init__(self, schema, sources=None, derivations=None):
        _validate_schema(schema)
        self._schema = schema

        if sources is None:
            self._sources = [EnvironmentConfig()]
        else:
            self._sources = sources

        self._derivations = derivations
        self._config = self._load_config()

    def _load_config(self):
        """Load configuration into Conifer."""
        config = _load_defaults(self._schema)

        for source in self._sources:
            source.load_config(self._schema)

        return config


def _load_defaults(schema):
    """Given a schema, load any default values from the schema"""
    return {}


def _validate_schema(schema):
    """Helper function to validate that the schema is itself valid."""
    schema_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json-schema.json')
    with open(schema_path, 'rb') as schema_file:
        json_schema = json.load(schema_file.read())

    validator = Draft4Validator(json_schema)
    validator.validate(schema)
