"""Click Wrapper module for Conifer

This module provides the `click_wrap` function, which enables users to expose their Conifer as
Click CLI options and consume them as a regular Conifer object.
"""
from functools import wraps, reduce

from .sources.click_opts import ClickOptionLoader
from .sources.schema_utils import iter_schema

def click_wrap(conf):
    """Wrap a function to provide Click options for a click command.

    Example:

        >>> import click
        >>> from conifer import Conifer
        >>> conf = Conifer(schema, [source, ...])

        >>> @click.command()
        >>> @conf.click_wrap()
        >>> def my_cmd(cli_conf):
        ...     click.secho(cli_conf)

        $ my_cmd --option value --nested-option value

    click_wrap behaves as if you have added individaul click.option flags for
    each configuration parameter in your Conifer schema, except it passes a
    populated Conifer object to the wrapped function rather than individual
    kwargs, allowing the CLI-provided configuration to be seamlessly combined
    with the rest of your app's configuration.

    Nested configuration sections are exposed by joining nested keys with the `-`
    character. All underscores will also be replaced with `-` by Click.

    Positional arguments are not supported, and defaults will be taken from
    your other Conifer configuration sources.

    CLI options will take precedence over all other Conifer-derived settings.

    Additional Click argument and option wrappers can be added as usual, before
    or after this wrapper. However, the cli_conf should always be the first
    parameter to the function, regardless of wrapper order. Click is weird.
    """
    # click is an optional dependency, required only for this method
    from click import option

    def decorator(fn):
        #
        # Create click options and store data that maps the internal kwarg name to
        # the created click.option and to the schema path location
        #
        click_options = {}
        schema_info = {}
        for schema_path, schema in iter_schema(conf._schema):
            option_flag = "--{}".format("-".join(schema_path).replace('_', '-'))
            option_kwarg_name = _get_option_name(option_flag)

            # Kwargs for this new click.option
            option_config = {}
            if schema.get("description"):
                option_config["help"] = schema.get("description")

            default = conf.get_in(schema_path)
            if default is not None:
                option_config["default"] = default
                option_config["show_default"] = True

            # TODO: can get fancy here and use schema to fill out more options for option
            #           http://click.palletsprojects.com/en/7.x/options/

            # The configured click.option decorator
            click_option = option(option_flag, **option_config)

            click_options[option_kwarg_name] = click_option
            schema_info[option_kwarg_name] = {
                    'schema': schema,
                    'schema_path': schema_path,
                }

        @wraps(fn)
        def wrapper(*args, **kwargs):
            #
            # Load click kwargs for this Conifer from the Cick CLI
            # Execute wrapped function with new Conifer poulated with CLI options
            #

            # kwargs added by other click.option wrappers
            stripped_kwargs = {k: v for k, v in kwargs.items() if k not in click_options}

            # User-populated CLI options for the Conifer
            values_from_click = {k: v for k, v in kwargs.items() if k in click_options}

            # The ClickOptionLoader initializes its data source from the
            # values added by the Click options
            click_loader = ClickOptionLoader(schema_info, values=values_from_click)

            # Creates copy of populated conf, adding the ClickOptionLoader
            new_conf = conf.override(sources=[click_loader])

            # Finally, call the original function, with its original args/kwargs,
            # but with the new conf passed as a positional
            fn(new_conf, *args, **stripped_kwargs)

        # Apply the new click option wrappers to the base wrapper
        # On the top of the call chain we expose the Click option flags,
        # but we convert those into a populated Conifer which gets passed
        # to the original function as a single positional
        click_wrapped = reduce(
            lambda fn, decorator: decorator(fn),  # recursively apply click option wrappers
            click_options.values(),  # click option wrappers
            wrapper,
        )  # initial value - base wrapper

        return click_wrapped

    return decorator


def _get_option_name(flag):
    """Derive the click kwarg name for the given option

    eg. --my-flag == my_flag
    """
    # We can't get it from click.option because the Option class is initialized in the inner
    # function
    from click.core import Option
    option = Option([flag])
    return option.name
