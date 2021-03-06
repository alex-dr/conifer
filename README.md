# conifer

Conifer is a library intended to make it simple to load configuration from multiple sources.

The user defines a configuration schema and possible sources, and conifer does the rest.

Conifer is still in initial development, but the functionality described in this document is implemented.

## Basic example

The default invocation of Conifer will load properties defined in your schema from the environment, using default values from your schema:

```python
from conifer import Conifer


schema = {
    'properties': {
        'foo': {
            'type': 'string',
            'default': 'bar',
        },
        'baz': {
           'type': 'string',
        },
    },
}

conf = Conifer(schema)

assert conf['foo'] == 'bar'
assert conf.get('baz', 'buz') == 'buz'
```

## Schema

Conifer uses JSON Schema Draft 4 ([json-schema.org](json-schema.org)) to define and validate your configuration.

The schema must be of type `object` and have defined `properites` which define your application's possible configuration keys.

## Sources

Conifer includes support for several sources out of the box, but users can easily create their own classes to provide arbitrary extensions of possible configuration sources.

Sources are defined by passing instantiated classes as an array to `Conifer`:

```python
from conifer.sources import JSONFileLoader, EnvironmentConfigLoader
conf = Conifer(schema,
               sources=[
                   JSONConfigLoader(path='/etc/myapp/config.json'),
                   JSONConfigLoader(path=os.path.expanduser('~/.myapp/config.json')),`
                   EnvironmentConfigLoader(prefix='MYAPP_')
                ])
```

The order of sources in this list represents the relative precedence of each source.
Values obtained by later sources supercede values obtained in earlier sources.
Values from the schema default are automatically loaded and considered to have the lowest precedence.

## Nested values

Conifer supports nested configuration values, or configuration 'sections'.

When inspecting configuration from your code, nested values can be obtained as objects (`conf['myobj'] == {'subkey': 'val'}`).

When a nested key has a default, it will only be defined if the parent object is defined.
For example, if you want a nested key `nestedkey` to always be defaulted, you would default its parent to `{}`:

```python
schema = {
    'properties': {
        'key': {
            'type': 'object',
            'properties': {
                'nestedkey': {
                    'type': 'string',
                    'default': 'foo'
                },
            }
            'default': {},
        },
    },
}
```

## Accessing values

The Conifer object behaves more or less like a regular dictionary object, allowing the usual `conf['myobj']['subkey']` syntax.

However, `__getattr__` is also overridden so users may also use the more convenient `conf.myobj.subkey` syntax.

When using attribute syntax, nested objects are returned as `conifer.conifer._AttrDict` objects, which inherit from `dict`.

## Derived values

For convenience, conifer also allows for a single layer of derived configuration values.
This allows you to use one or more resolved configuration values to define derived configuration values using arbitrary logic defined in user-supplied functions.

This feature can be used, as seen in the example, by passing a valid derivation dict to the keyword argument `derivations` when constructing a `Conifer` instance.

Derived keys are added to your original config object and can be nested.

If one of the supplied keys required for your derivation is not present in your resolved configuration, the derived key will not be added.

## Usage

For an example script, see [example.py](tests/example.py).

## Sources

### EnvironmentConfigLoader

This class loads values out of the environment, using the schema for hints on how to attempt to cast inputs into various types.

By default it will look for the keys in your configuration, joining nested keys with the `_` character.
You may optionally specify a prefix string by which all top-level keys will be prefixed, for example, the object

```python
EnvironmentConfig(prefix='MYAPP_')
```

It will successfully load the following key-value pairs for the schema used in the example above:

```bash
export MYAPP_PORT = '1234'  # loads as integer 1234
export MYAPP_LOGGING_VERBOSITY = WARN  # loads as string 'WARN'
export MYAPP_LOGGING_OUTPUT_FILE = ''  # loads as None, same as not setting it at all
export MYAPP_DEBUG_MODE = yes  # loads as boolean True
```

Booleans are loaded using yaml and then casting with Python's `bool()`.
Thus, valid values for a `False` result include, `0`, `no`, `FALSE`, and `false`.

Null values can be set with the strings `''`, `null`, `Null`, `NULL`, or by not defining the key, if the schema allows the value to be null or if it is not required.

### JSONFileLoader

This class loads values from JSON files.
Just give it a path to a file and conifer will do the rest!

Conifer will try to resolve an aboslute path, resolving `~` and `os.path.expandvars`.

### ClickOptionLoader

`click` is a popular tool for generating command line interfaces with a clean wrapper interface.

Conifer can be used to generate common command line flags for your app, allowing you to use the same environment variables, config files, and other configuration sources in tandem with your CLI options.

Let's see an example:

```python
import click
from conifer import Conifer, click_wrap


conf = Conifer(schema, ...)

@click.command()
@conf.click_wrap()
def my_cmd(cli_conf):
    """Print new conf with CLI params."""
    click.secho(cli_conf)
```

To enable `click_wrap`, you must have `click` installed.
You can install it with `pip install conifer[click]`, or including a compatible version of `click` in your application dependencies.
