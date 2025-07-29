"""Module with the visitor for the configuration model."""

from .config_model import (
    Author,
    ConfigProfile,
    ContainerConfiguration,
    DevelopmentEnvironment,
    ProjectInformation,
    SloughConfig,
)


class ConfigModelVisitor:
    """Visitor for the configuration model.

    The visitor traverses the configuration model and calls the corresponding
    methods for each element.
    """

    def visit_author(self, author: Author) -> None:
        """Visit the author information.

        Args:
            author (SloughConfigModel): The author information.
        """

    def visit_project_information(
        self, project_information: ProjectInformation
    ) -> None:
        """Visit the project information.

        Args:
            project_information (ProjectInformation): The project information.
        """

    def visit_development_environment(
        self, development_environment: DevelopmentEnvironment
    ) -> None:
        """Visit the development environment.

        Args:
            development_environment (DevelopmentEnvironment): The development
                environment.
        """

    def visit_container_configuration(
        self, container_configuration: ContainerConfiguration
    ) -> None:
        """Visit the container configuration.

        Args:
            container_configuration (ContainerConfiguration): The container
                configuration.
        """

    def visit_config_profile(self, config_profile: ConfigProfile) -> None:
        """Visit the configuration profile.

        Args:
            config_profile (ConfigProfile): The configuration profile.
        """

    def visit_slough_config(self, config_model: SloughConfig) -> None:
        """Visit the configuration model.

        Args:
            config_model (SloughConfig): The configuration model.
        """
