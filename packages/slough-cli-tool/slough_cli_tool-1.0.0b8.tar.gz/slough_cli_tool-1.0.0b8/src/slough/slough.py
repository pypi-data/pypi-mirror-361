"""Module with the Slough class."""

import logging
from types import TracebackType

from slough_config.config_model import (
    Author,
    ConfigProfile,
    ProjectInformation,
    SloughConfig,
)

from .exceptions import ConfigNotLoadedError
from .storage_manager import StorageManager


class Slough:
    """Class that represents a Slough application."""

    def __init__(self, storage_manager: StorageManager) -> None:
        """Initialize the Slough object.

        Args:
            storage_manager (StorageManager): The storage manager to use.
        """
        self._logger = logging.getLogger('Slough')
        self._storage_manager = storage_manager
        self._is_default_config = False
        try:
            self._config = self._storage_manager.load()
        except ConfigNotLoadedError:
            self._is_default_config = True
            self._config = self._get_default_config()

    def _get_default_config(self) -> SloughConfig:
        """Return a default configuration.

        Returns:
            SloughConfig: The default configuration.
        """
        return SloughConfig(
            project=ProjectInformation(
                name='empty_project',
                version='0.0.1',
                authors=[Author(name='nobody', email='nobody@nobody.com')],
            )
        )

    def __enter__(self) -> 'Slough':
        """Enter the context manager.

        Returns:
            Slough: The Slough object.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the context manager.

        Args:
            exc_type (type): The type of the exception.
            exc_value (Exception): The exception value.
            traceback (TracebackType): The traceback object.

        Returns:
            bool: True if the exception was handled, otherwise False.
        """
        if exc_type is None:
            self.save()
        return exc_type is None

    @property
    def config(self) -> SloughConfig:
        """Return the configuration.

        Returns:
            SloughConfig: The configuration.
        """
        return self._config

    @property
    def profile_list(self) -> list[str]:
        """Return a list with the profile names.

        Returns:
            list[str]: A list with the profile names.
        """
        return self._config.profile_list

    @property
    def is_default_config(self) -> bool:
        """Return True if the configuration is the default one.

        Returns:
            bool: True if the configuration is the default one, otherwise
            False.
        """
        return self._is_default_config

    def add_profile(self, profile_name: str) -> None:
        """Add a profile to the configuration.

        Args:
            profile_name (str): The name of the profile to add.
        """
        self._config.add_profile(profile_name)

    def remove_profile(self, profile_name: str) -> None:
        """Remove a profile from the configuration.

        Args:
            profile_name (str): The name of the profile to remove.
        """
        self._config.remove_profile(profile_name)

    def rename_profile(self, profile_name: str, new_name: str) -> None:
        """Remove a profile from the configuration.

        Args:
            profile_name (str): The name of the profile to rename.
            new_name (str): The new name for the profile.
        """
        self._config.rename_profile(profile_name, new_name)

    def get_profile(self, profile_name: str) -> ConfigProfile:
        """Get a profile from the configuration.

        Args:
            profile_name (str): The name of the profile to get.

        Returns:
            ConfigProfile: The profile.
        """
        return self._config.get_profile(profile_name)

    def get_profile_with_all(self, profile_name: str) -> ConfigProfile:
        """Get a profile from the configuration with the `_all` profile.

        Args:
            profile_name (str): The name of the profile to get.

        Returns:
            ConfigProfile: The profile combined with the `_all` profile.
        """
        return self._config.get_profile(profile_name).combine(
            self._config.get_profile('_all')
        )

    def save(self) -> None:
        """Save the configuration."""
        self._storage_manager.save(self._config)
