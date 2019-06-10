import json

from example import conf

from conifer import click_wrap

import click


@click.command("my_cmd")
@click.argument("before_arg")
@click.option("--before-option")
@click_wrap(conf)
@click.argument("after_arg")
@click.option("--after-option")
def my_cmd(cli_conf, before_arg, after_arg, before_option=None, after_option=None):
    """My fun command.

    cli_conf must always be the first positional argument to the wrapped function, regardless
    of order of wrappers in the definition.

    Click somehow forces the order to be that way.
    """
    click.secho(json.dumps(cli_conf._config, indent=4))
    click.secho("before: {}, after: {}".format(before_arg, after_arg))


if __name__ == "__main__":
    my_cmd()
