"""Exceptions for slough_config module."""


class SloughConfigError(Exception):
    """Base class for all exceptions in the slough_config module."""


class ProfileNotFoundError(SloughConfigError):
    """Exception raised when a profile is not found in the configuration."""


class InvalidProfileNameError(SloughConfigError):
    """Exception raised when a profile name is invalid."""


class DuplicateProfileNameError(SloughConfigError):
    """Exception raised when a profile name is double."""


class DefaultProfileError(SloughConfigError):
    """Exception raised when a default profile is being altered."""


class InvalidPlatformError(SloughConfigError):
    """Exception raised when a platform is invalid."""
