class EnvironmentConfigLoader(object):
    """Loader for environment variables."""

    def __init__(self, prefix=''):
        self._prefix = prefix

    def load_config(self, schema):
        """Load configuration values for this schema."""
        pass
