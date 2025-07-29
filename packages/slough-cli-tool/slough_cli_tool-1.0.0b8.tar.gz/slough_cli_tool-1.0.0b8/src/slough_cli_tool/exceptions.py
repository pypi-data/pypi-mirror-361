"""Module with custom exceptions for the Slough CLI package."""


class SloughCLIError(Exception):
    """Base exception for the Slough CLI package."""


class ConfigAlreadySetError(SloughCLIError):
    """Error raised when the configuration is already set."""


class OutputTypeUnsupportedError(SloughCLIError):
    """Error raised when the output type is not supported."""
