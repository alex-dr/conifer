# builtin
from copy import deepcopy
import json
import os

# third party
from jsonschema import Draft4Validator, validators

# this package
from .sources import EnvironmentConfigLoader
from .utils import get_in, recursive_update, set_in


class Conifer(object):
    """Conifer is an object to encapsulate your application's configuration.

    Conifer is instantiated with a schema and possible configuration sources.

    By default, Conifer will use the built-in EnvironmentConfigLoader source only.
    """

    # The populated configuration data, should be a plain dict
    _config = None

    def __init__(self, schema, sources=None, derivations=None):
        # ensure we have a valid JSON Schema
        _validate_schema(schema)
        self._schema = schema

        DefaultSettingValidator = _extend_with_default(Draft4Validator)
        # update self._config with default values from the schema
        self._config = {}
        DefaultSettingValidator(schema).validate(self._config)

        self._validator = Draft4Validator(self._schema)

        if sources is None:
            self._sources = [EnvironmentConfigLoader()]
        else:
            self._sources = sources

        self._derivations = derivations

        self.update_config()

    def update_config(self):
        """Load or re-load configuration from defined sources.

        Called in __init__, but can be called at any time to reload all configuration.

        Side Effects
        ------------
        modifies self._config
        """
        new_config = _update_config(self._config, self._schema, self._sources, self._derivations)
        self._validator.validate(new_config)
        recursive_update(self._config, new_config)

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


def _iter_derivations(derivations):
    """Walk through derivations which may be nested.

    Return (['nested', 'key'], value).
    """
    if derivations is not None:
        for key, value in derivations.iteritems():
            if 'derivation' not in value:
                for subkey, sub_value in _iter_derivations(value):
                    yield ([key] + subkey, sub_value)
            else:
                yield ([key], value)


def _derive_values(config, derivations):
    """Use derivation rules to determine derived config values."""
    derived_config = {}
    for key, value in _iter_derivations(derivations):
        param_keys = value['parameters']
        try:
            params = [get_in(config, param_key) for param_key in param_keys]
        except KeyError:
            continue
        else:
            result = value['derivation'](*params)
            set_in(derived_config, key, result)

    return derived_config


def _extend_with_default(validator_class):
    """Enable the supplied JSON Schema validator to set default values when performing validation.

    Updates the validator such that when `validate` is called, the object will be modifed to
    add default values for properties.

    The default values must comply with the validation schema.

    From: http://python-jsonschema.readthedocs.io/en/latest/faq/
    """
    validate_properties = validator_class.VALIDATORS['properties']

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if 'default' in subschema:
                instance.setdefault(property, subschema['default'])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {'properties': set_defaults},
    )


def _update_config(existing_config, schema, sources, derivations):
    """Gather configuration and derived values from sources.

    Derived values must include the existing configuration, but
    we don't want to modify the class's config in this method in order
    to make the class method atomic.
    """
    config = deepcopy(existing_config)

    for source in sources:
        new_data = source.load_config(schema)
        recursive_update(config, new_data)

    derived_values = _derive_values(config, derivations)
    recursive_update(config, derived_values)

    return config


def _validate_schema(schema):
    """Helper function to validate that the schema is itself valid."""
    schema_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json-schema.json')
    with open(schema_path, 'rb') as schema_file:
        json_schema = json.load(schema_file)

    validator = Draft4Validator(json_schema)
    validator.validate(schema)

    if 'properties' not in schema:
        raise ValueError('Invalid schema: must have `properties` key')
