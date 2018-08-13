# builtin
import json
import os

# third party
from jsonschema import Draft4Validator, validators

# this package
from .sources import EnvironmentConfig


class Conifer(object):
    """Conifer is an object to encapsulate your application's configuration.

    Conifer is instantiated with a schema and possible configuration sources.

    By default, Conifer will use the built-in EnvironmentConfig source only.
    """

    # The populated configuration data
    _config = None

    def __init__(self, schema, sources=None, derivations=None):
        _validate_schema(schema)
        self._schema = schema
        default_setting_validator = _extend_with_default(Draft4Validator(schema))
        self._validator = default_setting_validator

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

    def __getitem__(self, key):
        return self._config[key]


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


def _extend_with_default(validator_class):
    """Enable the supplied JSON Schema validator to set default values when performing validation.

    Updates the validator such that when `validate` is called, the object will be modifed to
    add default values for properties which are not defined.

    The default values must comply with the validation schema.

    From: http://python-jsonschema.readthedocs.io/en/latest/faq/
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {'properties': set_defaults},
    )
