"""Module with custom exceptions for the Slough package."""


class SloughError(Exception):
    """Base exception for the Slough package."""


class StorageManagerError(SloughError):
    """Base exception for the storage manager."""


class ConfigNotLoadedError(StorageManagerError):
    """Exception raised when the configuration is not loaded."""
