"""Conifer example usage script

While not exhaustive, this example illustrates the basic usage of Conifer
with light annotations

The variable names used are only intended to be suggestive of things a real
user of Conifer might want to configure.

It is tested with test_example.py, so it's useful as an end to end test.
"""
import os

from conifer import Conifer
from conifer.sources import DictLoader, EnvironmentConfigLoader, JSONFileLoader


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
JSON_PATH = os.path.join(THIS_DIR, "example.json")

schema = {
    "$schema": "http://json-schema.org/draft-04/schema",  # meta-schema for this object
    "title": "My apps configuration schema",  # optional - unused by conifer
    "description": (
        "This is a Draft 04 JSON schema document describing valid configuration"
        " options for this application."
    ),  # optional - unused by conifer
    "type": "object",  # optional
    "properties": {  # required
        "LOGGING": {
            "description": "Options pertaining to logging for myapp",
            "type": "object",
            "properties": {
                "VERBOSITY": {
                    "description": "Logging verbosity for myapp",
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARN", "ERROR"],
                    "default": "INFO",
                },
                "OUTPUT_FILE": {
                    "description": "(optional) Absolute or relative file path for logging",
                    "type": ["string", "null"],
                },
            },
            "default": {},  # required for nested defaults to be defaulted
        },
        "DICT_OVERRIDE": {
            "description": "Key to override from dict loader",
            "type": "string",
            "default": "original",
        },
        "DEBUG_MODE": {
            "description": "Enable debug mode for my Flask app",
            "type": "boolean",
            "default": False,
        },
        "PORT": {
            "description": "Port the application will listen on",
            "type": "integer",
            "minimum": 1,
            "maximum": 65534,
            "default": 8080,
        },
    },
}

# Derived values are useful to avoid code repetition in other parts of your app.
derivations = {
    "DEBUG_PORT": {
        "description": "Port the application will use for serving debug requests",  # optional
        "derivation": lambda port: port + 1,
        "parameters": ["PORT"],
    },
    "LOGGING": {
        "OUTPUT_FILE_VERBOSITY": {
            "derivation": lambda verbosity, logfile: logfile + "_" + verbosity,
            "parameters": [["LOGGING", "VERBOSITY"], ["LOGGING", "OUTPUT_FILE"]],
        }
    },
}

data_dict = {"DICT_OVERRIDE": "overridden"}

conf = Conifer(
    schema,
    sources=[
        DictLoader(data_dict),
        JSONFileLoader(path=JSON_PATH),
        EnvironmentConfigLoader()],
    derivations=derivations,
)


def main():
    print(conf._config)
    # values from schema are set
    assert conf["DEBUG_MODE"] is False
    assert conf["PORT"] == 8080
    assert conf["LOGGING"]["VERBOSITY"] == "INFO"
    # derived values are set
    assert conf.get("DEBUG_PORT", None) == conf["PORT"] + 1
    assert conf.LOGGING.OUTPUT_FILE_VERBOSITY == "/my/log_INFO"
    assert conf.LOGGING["OUTPUT_FILE_VERBOSITY"] == "/my/log_INFO"
    # create separate config in new namespace
    os.environ["MYAPP_PORT"] = "1234"
    other_conf = conf.override(sources=[EnvironmentConfigLoader(prefix="MYAPP_")])
    assert other_conf.PORT == 1234
    # derivations are copied over and re-calculated
    assert other_conf.DEBUG_PORT == 1235
    assert conf.DICT_OVERRIDE == "overridden"


if __name__ == "__main__":
    main()
