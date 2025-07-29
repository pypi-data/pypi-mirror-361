"""Module with the model for the configuration file."""

import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

from .exceptions import (
    DefaultProfileError,
    DuplicateProfileNameError,
    InvalidPlatformError,
    InvalidProfileNameError,
    ProfileNotFoundError,
)

if TYPE_CHECKING:  # pragma: no cover
    from .config_model_visitor import ConfigModelVisitor


class SloughConfigModel(ABC, BaseModel, validate_assignment=True):
    """Base class for a Slough configuration model.

    Contains the `visit` method to traverse the model.
    """

    @abstractmethod
    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor to call.
        """


class Author(SloughConfigModel):
    """Model for the author information.

    Attributes:
        name (str): The name of the author.
        email (str): The email address of the author. Must match the specified
            pattern.
    """

    name: str
    email: str = Field(pattern=r'^\S+@\S+\.\S+$')

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_author(self)


class ProjectInformation(SloughConfigModel):
    """Model for the project information.

    Attributes:
        name (str): The name of the project.
        version (str): The version of the project. Must follow semantic
            versioning.
        authors (list[Author]): A list of authors involved in the project.
    """

    name: str
    version: str = Field(pattern=r'^(\d+)\.(\d+)\.(\d+)(?:-\S+\d+)?$')
    authors: list[Author]

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_project_information(self)


class DevelopmentEnvironment(str, Enum):
    """Enum for the development environment.

    Attributes:
        PYTHON_GENERIC (str): Represents a generic Python development
            environment.
        NODEJS_GENERIC (str): Represents a generic Node.js development
            environment.
    """

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_development_environment(self)

    CPP_GENERIC = 'cpp-generic'
    GENERIC = 'generic'
    NODEJS_GENERIC = 'nodejs-generic'
    PYTHON_GENERIC = 'python-generic'
    RUST_GENERIC = 'rust-generic'
    LISP_SCHEME_GENERIC = 'lisp-scheme-generic'
    JAVA_GENERIC = 'java-generic'
    ASM6502_GENERIC = 'asm6502-generic'
    ESP32_GENERIC = 'esp32-generic'


class ContainerConfiguration(SloughConfigModel):
    """Configuration for a container.

    Attributes:
        tags (list[str] | None): A list of tags for the container.
    """

    tags: list[str] = []
    registry: str | None = Field(
        default=None, pattern=r'^[a-zA-Z0-9.-]+(:\d+)?(\/[a-zA-Z._/-]+)?$'
    )
    image: str | None = Field(
        default=None,
        pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_.-]+$',
    )
    platforms: list[str] = Field(
        default=[],
        description='List of platforms to build for',
    )

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_container_configuration(self)

    def combine(
        self, other: Optional['ContainerConfiguration']
    ) -> 'ContainerConfiguration':
        """Combine this model with another model of the same type.

        Args:
            other (ContainerConfiguration): The other model to combine with.
        """
        object_copy = self.model_copy(deep=True)
        if other is not None:
            object_copy.tags.extend(other.tags)
            object_copy.tags = list(set(object_copy.tags))
            object_copy.platforms.extend(other.platforms)
            object_copy.platforms = list(set(object_copy.platforms))
            object_copy.registry = other.registry or object_copy.registry
            object_copy.image = other.image or object_copy.image
        return object_copy

    def add_tags(self, tags: str | list[str]) -> None:
        """Add tags to the container configuration.

        Args:
            tags (str | list[str]): The tag or tags to add.
        """
        if isinstance(tags, str):
            tags = [tags]
        self.tags.extend([tag.lower() for tag in tags])
        self.tags = list(set(self.tags))

    def remove_tags(self, tags: str | list[str]) -> None:
        """Remove tags from the container configuration.

        Args:
            tags (str | list[str]): The tag or tags to remove.
        """
        if isinstance(tags, str):
            tags = [tags]
        tags = [tag.lower() for tag in tags]
        self.tags = list(filter(lambda t: t.lower() not in tags, self.tags))

    def add_platforms(self, platforms: str | list[str]) -> None:
        """Add platforms to the container configuration.

        Args:
            platforms (str | list[str]): The platform or platforms to add.
        """
        allowed_platforms = [
            'linux/amd64',
            'linux/arm64',
            'linux/arm/v7',
            'linux/arm/v6',
            'linux/ppc64le',
            'linux/s390x',
            'linux/386',
        ]
        if isinstance(platforms, str):
            platforms = [platforms]
        for platform in platforms:
            if platform not in allowed_platforms:
                raise InvalidPlatformError(
                    f'Invalid platform name: "{platform}".'
                )
        self.platforms.extend([platform.lower() for platform in platforms])
        self.platforms = list(set(self.platforms))

    def remove_platforms(self, platforms: str | list[str]) -> None:
        """Remove platforms from the container configuration.

        Args:
            platforms (str | list[str]): The platform or platforms to remove.
        """
        if isinstance(platforms, str):
            platforms = [platforms]
        platforms = [platform.lower() for platform in platforms]
        self.platforms = list(
            filter(lambda p: p.lower() not in platforms, self.platforms)
        )


class ConfigProfile(SloughConfigModel):
    """Model for the configuration profile.

    Contains all settins for a specific project.

    Attributes:
        container (ContainerConfiguration | None): The container configuration.
    """

    container: ContainerConfiguration | None = None

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_config_profile(self)

    def combine(self, other: 'ConfigProfile') -> 'ConfigProfile':
        """Combine this model with another model.

        Args:
            other (CombinableSloughConfigModel): The other model to combine
                with.
        """
        if self.container is None:
            self.container = ContainerConfiguration()
        return ConfigProfile(container=self.container.combine(other.container))

    def get_container_configuration(self) -> ContainerConfiguration:
        """Get the container configuration.

        Returns:
            ContainerConfiguration: The container configuration.
        """
        if self.container is None:
            self.container = ContainerConfiguration()
        return self.container


class SloughConfig(SloughConfigModel):
    """Model for the configuration file.

    Attributes:
        project (ProjectInformation): The project information.
        development_environment (DevelopmentEnvironment | None): The
            development environment, if specified.
    """

    project: ProjectInformation
    development_environment: DevelopmentEnvironment | None = None
    cfg_profiles: dict[str, ConfigProfile] = {
        '_default': ConfigProfile(),
        '_all': ConfigProfile(),
    }

    def visit(self, visitor: 'ConfigModelVisitor') -> None:
        """Visit the model element.

        Args:
            visitor (ConfigModelVisitor): The visitor method to call.
        """
        visitor.visit_slough_config(self)

    @property
    def profile_list(self) -> list[str]:
        """List of profile names.

        Returns:
            list[str]: A list of profile names.
        """
        return list(self.cfg_profiles.keys())

    def add_profile(self, profile_name: str) -> None:
        """Create a new configuration profile.

        Will create a new profile with the specified name if it does not exist.
        The name is validated against the pattern.

        Args:
            profile_name (str): The name of the profile to create.
        """
        if not self._is_valid_profile_name(profile_name):
            raise InvalidProfileNameError(
                'Invalid profile name. Only alphanumeric characters, '
                'dashes, and underscores are allowed.'
            )

        if self._profile_exists(profile_name):
            raise DuplicateProfileNameError(
                f'Profile "{profile_name}" already exists.'
            )

        self.cfg_profiles[profile_name] = ConfigProfile()

    def _is_valid_profile_name(self, profile_name: str) -> bool:
        """Check if the profile name is valid.

        Args:
            profile_name (str): The name of the profile to check.

        Returns:
            bool: True if the profile name is valid, False otherwise.
        """
        return re.match(r'^[a-zA-Z][A-Za-z0-9_-]+$', profile_name) is not None

    def remove_profile(self, profile_name: str) -> None:
        """Remove a configuration profile.

        Will remove the profile with the specified name if it exists.

        Args:
            profile_name (str): The name of the profile to remove.
        """
        if not self._profile_exists(profile_name):
            raise ProfileNotFoundError(
                f'Profile "{profile_name}" does not exist.'
            )

        if profile_name in ['_default', '_all']:
            raise DefaultProfileError(
                f'Profile "{profile_name}" cannot be removed.'
            )

        del self.cfg_profiles[profile_name]

    def _profile_exists(self, profile_name: str) -> bool:
        """Check if a profile exists.

        Args:
            profile_name (str): The name of the profile to check.

        Returns:
            bool: True if the profile exists, False otherwise.
        """
        return profile_name in self.cfg_profiles

    def rename_profile(self, profile_name: str, new_name: str) -> None:
        """Rename a profile.

        Will rename the profile with the specified name if it exists.

        Args:
            profile_name (str): The name of the profile to rename.
            new_name (str): The new name for the profile.
        """
        if not self._is_valid_profile_name(new_name):
            raise InvalidProfileNameError(
                'Invalid profile name. Only alphanumeric characters, '
                'dashes, and underscores are allowed.'
            )

        if not self._profile_exists(profile_name):
            raise ProfileNotFoundError(
                f'Profile "{profile_name}" does not exist.'
            )

        if self._profile_exists(new_name):
            raise DuplicateProfileNameError(
                f'Profile "{new_name}" already exists.'
            )

        self.cfg_profiles[new_name] = self.cfg_profiles.pop(profile_name)

    def get_profile(self, profile_name: str) -> ConfigProfile:
        """Get a profile.

        Will return the profile with the specified name if it exists.

        Args:
            profile_name (str): The name of the profile to get.

        Raises:
            ValueError: If the profile does not exist.
        """
        if not self._profile_exists(profile_name):
            raise ProfileNotFoundError(
                f'Profile "{profile_name}" does not exist.'
            )

        return self.cfg_profiles[profile_name]
