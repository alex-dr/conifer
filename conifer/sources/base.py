import yaml

from jsonschema import Draft4Validator


class CoercionError(Exception):
    pass


def nest_value(key, value):
    """Take an array key representation and return it as a nested object

    Key is taken as a list of keys for nested values
    """
    if len(key) == 1:
        return {key[0]: value}
    else:
        return {key[0]: nest_value(key[1:], value)}


def iter_schema(schema):
    """Return resolved key names with schemas for all keys.

    Generator yielding (key_name, schema) where key_name is a list of
    keys indicating nesting, eg

    (['outer', 'inner', 'nested'], {'type': 'string'})
    """
    validator = Draft4Validator(schema)
    for key, value in schema.get('properties', {}).iteritems():
        if value.get('$ref'):
            value.update(validator.resolver.resolve(value.get('$ref'))[1])
        if value.get('type') == 'object':
            for subkey, sub_value in iter_schema(value):
                yield ([key] + subkey, sub_value)
        else:
            yield ([key], value)


def coerce_value(value, schema):
    """Attempt to coerce a value to a valid schema-defined type.

    We're doing our best here folks, if it doesn't work, your schema
    may be more complicated than you need it to be...
    """
    validator = Draft4Validator(schema)
    value_type = type(value)
    schema_type = schema.get('type')

    if isinstance(schema_type, str):
        coerced_value = _coercion_matrix[value_type][schema_type](value)
        validator.validate(coerced_value)
        return coerced_value

    schema_allof = schema.get('allOf')
    schema_anyof = schema.get('anyOf')
    schema_oneof = schema.get('oneOf')

    def coerce_iterable(schemas, stop_on_valid=True):
        last_exception = None
        for desirable_type in schemas:
            try:
                coerced_value = _coercion_matrix[value_type][desirable_type](value)
                # Try to validate; if we can't maybe we can try another type
                validator.validate(coerced_value)
            except Exception as last_exception:
                # Not coercing to the first option is not unexpected
                pass
            # raise last exception with traceback
            if last_exception:
                raise
            else:
                if stop_on_valid:
                    return coerced_value
        return coerced_value

    if isinstance(schema_type, list):
        return coerce_iterable(schema_type)

    if schema_anyof is not None:
        return coerce_iterable(schema['anyOf'])

    if schema_allof is not None:
        return coerce_iterable(schema['allOf'], stop_on_valid=False)

    if schema_oneof is not None:
        return coerce_iterable(schema['oneOf'])


def _string_to_array(value):
    """Attempt to divine an array from what we got."""
    return map(lambda x: x.strip(), value.split(','))


def _string_to_bool(value):
    """Attempt to coerce to boolean value

    Accepts lots of stuff from the yaml spec, like 0, yes, no, TRUE, etc
    """
    return bool(yaml.load(value))


def _string_to_object(value):
    value = yaml.safe_load(value)
    if not isinstance(value, dict):
        raise CoercionError('Could not coerce string \'{}\' to dict'.format(value))


def _coerce_to_number(value):
    """Attempt to coerce to a 'number' value.

    Since json schema spec is loose here, we'll return the int value
    if it's equal to the float value, otherwise give you a float.
    """
    if int(value) == float(value):
        return int(value)
    return float(value)


def _raise_coercion_error(value, desired_type):
    value_type = type(value)
    raise CoercionError('Could not cast value {} of type {} '
                        'to type {}'.format(value, value_type, desired_type))


# Dict of all coercions we can perform based on valid jsonschema simple types
_coercion_matrix = {
    str: {
        'array': _string_to_array,
        'boolean': _string_to_bool,
        'integer': lambda x: int(x),
        'number': _coerce_to_number,
        'object': _string_to_object,
        'string': lambda x: x,
    },
    int: {
        'array': lambda x: [x],
        'boolean': lambda x: bool(x),
        'integer': lambda x: x,
        'number': _coerce_to_number,
        'object': lambda x: _raise_coercion_error(x, 'object'),
        'string': lambda x: str(x),
    },
    list: {
        'array': lambda x: x,
        'boolean': lambda x: bool(x),
        'integer': lambda x: _raise_coercion_error(x, 'integer'),
        'number': lambda x: _raise_coercion_error(x, 'number'),
        'object': lambda x: _raise_coercion_error(x, 'object'),
        'string': lambda x: str(x),
    },
}
