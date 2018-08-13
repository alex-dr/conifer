conifer
=======

Conifer is a library intended to make it simple to load configuration from multiple sources.

The user defines a configuration schema and possible sources, and conifer does the rest.

Schema
------

Conifer uses JSON Schema ([json-schema.org](json-schema.org)) to validate your configuration.

The schema must be of type `object` and have defined `properites` which define your application's possible configuration keys.

Nested values
-------------

Conifer supports nested configuration values, or configuration 'sections'.

When a given configuration source does not naturally supply a means of nesting, keys and sub-keys are joined with the '.' character.
In the example below, this means the logging verbosity can be set with the environment variable `MYAPP_LOGGING.VERBOSITY`.

Derived values
--------------

For convenience, conifer also allows for a single layer of derived configuration values.
This allows you to use one or more resolved configuration values to define derived configuration values using arbitrary logic defined in user-supplied functions.

Usage
-----

```python
from conifer import Conifer


schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#'  # meta-schema for this object
    'title': 'My apps configuration schema',
    'description': ('This is a Draft 04 JSON schema document describing valid configuration'
                    ' options for this application.'),
    'type': 'object',
    'properites': {
        'LOGGING': {
            'description': 'Options pertaining to logging for myapp',
            'type': 'object',
            'properties': {
                'VERBOSITY': {
                    'description': 'Logging verbosity for myapp',
                    'type': 'string',
                    'enum': ['DEBUG', 'INFO', 'WARN', 'ERROR'],
                    'default': 'INFO'
                },
                'OUTPUT_FILE': {
                    'description': '(optional) Absolute or relative file path for logging',
                    'type': ['string', 'null']
                },
            },
        },
        'DEBUG_MODE': {
            'description': 'Enable debug mode for my Flask app',
            'type': 'boolean',
            'default': False
        },
        'PORT': {
            'description': 'Port the application will listen on',
            'type': 'integer',
            'minimum': 1,
            'maximum': 65534,
            'default': 8080
        }
    }
}

derivations = {
    'DEBUG_PORT': {
        'description': 'Port the application will use for serving debug requests',
        'derivation': lambda myapp_port: myapp_port + 1,
        'parameters': ['PORT'],
    }
}

conf = Conifer(
    schema,
    derivations=derivations,
)

app = Flask()

if __name__ == '__main__':
    app.run(port=conf['MYAPP_PORT'], debug=conf['MAPP_DEBUG_MODE'])
```

EnvironmentConfig
-----------------

This class loads values out of the environment, using the schema for hints on how to attempt to cast inputs into various types.

By default it will look for the keys in your configuration, joining nested keys with the `.` character.
You may optionally specify a prefix string by which all top-level keys will be prefixed, for example, the object

```python
EnvironmentConfig(prefix='MYAPP.')
```

It will successfully load the following key-value pairs for the schema used in the example above:

```bash
export MYAPP.PORT = '1234'  # loads as integer 1234
export MYAPP.LOGGING.VERBOSITY = WARN  # loads as string 'WARN'
export MYAPP.LOGGING.OUTPUT_FILE = ''  # loads as None, same as not setting it at all
export MYAPP.DEBUG_MODE = yes  # loads as boolean True
```

Booleans are loaded using yaml and then casting with Python's `bool()`.
Thus, valid values for a `False` result include, `0`, `no`, `FALSE`, and `false`.

Null values can be set with the strings `''`, `null`, `Null`, `NULL`, or by not defining the key, if the schema allows the value to be null or if it is not required.
