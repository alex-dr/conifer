from .schema_utils import coerce_value, nest_value

from conifer.utils import recursive_update


class ClickOptionLoader(object):
    """Loads config from click.command CLI.

    Only intended for internal use by the click_wrap utility."""

    def __init__(self, schema_info, values=None):
        self.schema_info = schema_info
        self.values = values

    def load_config(self, schema):
        #
        # This one goes a little backwards because we don't iterate the schema to discover
        # possible keys. Instead, we iterate over keys we have values for and store them
        # using our stored info about how keys map to the schema
        #
        partial_config = {}
        for parameter_key, raw_value in self.values.items():
            coerced_value = coerce_value(
                raw_value, self.schema_info[parameter_key]["schema"]
            )

            if coerced_value is not None:
                new_data = nest_value(
                    self.schema_info[parameter_key]["schema_path"], coerced_value
                )

                recursive_update(partial_config, new_data)

        return partial_config
