"""Base class module for config sources/loaders."""
from enum import Enum


class LoaderMode(Enum):
    """Enum for specifying types of access a given loader has to its store."""

    # Read-Only access
    RO = 1
    # Read-Write access
    RW = 2
    # Write-Only access
    WO = 3


class LoaderDisallowedAction(Exception):
    """Client asked us to disallow this action."""

    pass


class BaseLoader(object):
    """Generic loader"""

    def __init__(self, mode=LoaderMode.RO, **kwargs):
        """Initialize loader.

        Parameters
        ----------
        mode : LoaderMode
        """
        self.mode = mode

    def load_config(self, schema):
        """Load configuration values for this schema.

        Can perform a lookup of possible config settings or simply load all of
        the data in a source. Be careful with the latter - additional config
        settings may be present in the source and fail validation. For example
        grabbing all possible environment values is likely to not work.

        Should not load settings which are deemed to be empty or null-valued.

        Parameters
        ----------
        schema : dict
            Draft 4 JSON Schema loaded as Python dict

        No additional parameters may be passed

        Returns
        -------
        dict : subset of the schema configuration present in the source.
        """
        if self.mode in (LoaderMode.RO, LoaderMode.RW):
            return self._load_config(schema)
        else:
            raise LoaderDisallowedAction(
                "This loader was not initialized with read permissions! Mode is {}".format(
                    self.mode
                )
            )

    def _load_config(self, schema):
        """Implementation of load_config."""
        raise NotImplementedError()

    def set_config(self, data):
        """Store validated config into backing store.

        Configuration will already be validated when calling this method.

        Stores which may have one or more clients should take care to enforce
        atomicity of update. This is not recommended to be implemented for
        file or environment variable sources.

        Parameters
        ----------
        data : dict
            Pre-validated data to store
        """
        if self.mode in (LoaderMode.WO, LoaderMode.RW):
            return self._set_config(data)
        else:
            raise LoaderDisallowedAction(
                "This loader was not initialized with read permissions! Mode is {}".format(
                    self.mode
                )
            )

        raise NotImplementedError()

    def _set_config(self, schema):
        """Implementation of set_config."""
        raise NotImplementedError()
