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

    On instantiation, Conifer will immediately load configuration from all configured sources,
    unless `skip_load_on_init` is set to True. In the latter case, `self.update_config` must be
    called manually after instantiation.

    Derivations:
        Derivations enable defining additional configuration based on the
        conifer config values loaded from all sources, enabling an extra layer of configuration.
        You must supply a new key name, the config options it depends on, and a function
        taking the values of those options to return the derived value.

        Derived values are exposed in the final Conifer object
        Derivations are supplied as a dictionary of the format

            'KEY': {
                'description': 'helpful text',
                'derivation': lambda x, y: x + y,
                'parameters': [['KEY'], ['NESTED', 'KEY']],
            }

    Parameters
    ----------
    schema : dict
        JSONSchema Draft 4 compatible schema definition

    Kwargs
    ------
    sources : list
        List of configured source objects (eg. EnvironmentConfigLoader). Sources are loaded in
        the order passed, with the final elements taking precedence over the first.
    derivations : dict
        Dict of derivation functions
    initial_config : dict
        Pre-load default values for conifguration. These values will be overridden by any sources,
        including schema defaults.
    skip_load_on_init : bool (False)
         Skip loading configuration during `__init__`
    """

    # The populated configuration data, should be a plain dict
    _config = None

    def __init__(
        self,
        schema,
        sources=None,
        derivations=None,
        initial_config=None,
        skip_load_on_init=False,
    ):
        # ensure we have a valid JSON Schema
        _validate_schema(schema)
        self._schema = schema

        DefaultSettingValidator = _extend_with_default(Draft4Validator)
        self._config = initial_config or {}
        # update self._config with default values from the schema
        # since this uses setdefault, it shouldn't override initial_config
        DefaultSettingValidator(schema).validate(self._config)

        self._validator = Draft4Validator(self._schema)

        if sources is None:
            self._sources = [EnvironmentConfigLoader()]
        else:
            self._sources = sources

        self._derivations = derivations

        if not skip_load_on_init:
            self.update_config()

    def update_config(self):
        """Load or re-load configuration from defined sources.

        Called in __init__, but can be called at any time to reload all configuration.

        Side Effects
        ------------
        modifies self._config
        """
        new_config = _update_config(
            self._config, self._schema, self._sources, self._derivations
        )
        self._validator.validate(new_config)
        recursive_update(self._config, new_config)

    def override(self, sources=None):
        """Create a new Conifer with additional overrides from provided sources

        Does not modify passed conf instance.

        Parameters
        ----------
        sources : list
            List of instantiated loader classes
        derivations : dict
            Dict of derivations

        Returns
        -------
        Conifer
        """
        new_conf = Conifer(
            self._schema,
            sources=sources,
            derivations=self._derivations,
            initial_config=self._config,
        )
        return new_conf

    def __getitem__(self, key):
        return self._config[key]

    def __getattr__(self, key):
        return _AttrDict(self._config).__getattr__(key)

    def get(self, key, default=None):
        """Get value, default, or None."""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def get_in(self, key, default=None):
        try:
            get_in(self._config, key)
        except KeyError:
            return default


class _AttrDict(dict):
    """Dict with mild overrides so we can use keys as attributes."""

    _dict = None

    def __init__(self, dic):
        super(_AttrDict, self).__init__(dic)
        self._dict = dic

    def __getattr__(self, key):
        value = self._dict.get(key)
        if value is None:
            raise AttributeError(
                "{self} object has no such attribute {key}".format(**locals())
            )

        if isinstance(value, dict):
            return _AttrDict(value)

        return value


def _iter_derivations(derivations):
    """Walk through derivations which may be nested.

    Return (['nested', 'key'], value).
    """
    if derivations is not None:
        for key, value in derivations.items():
            if "derivation" not in value:
                for subkey, sub_value in _iter_derivations(value):
                    yield ([key] + subkey, sub_value)
            else:
                yield ([key], value)


def _derive_values(config, derivations):
    """Use derivation rules to determine derived config values."""
    derived_config = {}
    for key, value in _iter_derivations(derivations):
        param_keys = value["parameters"]
        try:
            params = [get_in(config, param_key) for param_key in param_keys]
        except KeyError:
            # If key is not defined, don't try to derive a value
            continue
        else:
            result = value["derivation"](*params)
            set_in(derived_config, key, result)

    return derived_config


def _extend_with_default(validator_class):
    """Enable the supplied JSON Schema validator to set default values when performing validation.

    Updates the validator such that when `validate` is called, the object will be modifed to
    add default values for properties.

    The default values must comply with the validation schema.

    From: http://python-jsonschema.readthedocs.io/en/latest/faq/
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})


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
    schema_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "json-schema.json"
    )
    with open(schema_path, "rb") as schema_file:
        json_schema = json.load(schema_file)

    validator = Draft4Validator(json_schema)
    validator.validate(schema)

    if "properties" not in schema:
        raise ValueError("Invalid schema: must have `properties` key")
