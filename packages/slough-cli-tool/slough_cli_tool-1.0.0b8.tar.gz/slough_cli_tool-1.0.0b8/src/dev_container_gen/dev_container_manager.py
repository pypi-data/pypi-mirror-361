"""Module with a class to manage a devcontainer.json file."""

from pathlib import Path

from .loader import Loader
from .model import DevContainer
from .saver import Saver


class DevContainerManager:
    """Class to manage a devcontainer.json file."""

    def __init__(self, default_name: str) -> None:
        """Initialize the DevContainerManager class."""
        self._config_filename = self._get_dev_container_config_filename()

        # Dependencies
        self._loader = Loader(path=self._config_filename)
        self._saver = Saver(path=self._config_filename)

        # Dev container configuration model
        self._default_name = default_name
        self._dev_container_config: DevContainer = (
            self._get_existing_configuration()
        )

    def save(self) -> None:
        """Save the confifguration to the correct location."""
        self._saver.save(self._dev_container_config)

    def update_configuration(
        self,
        image: str,
        name: str | None = None,
        bind_docker_socket: bool | None = None,
        tag: str = 'latest',
    ) -> None:
        """Updates the development container configuration.

        Args:
            image (str): The container image to use in the configuration.
            name (str | None): The name for the dev container. If None, the
                existing name in the configuration is retained.
            bind_docker_socket (bool | None): Whether to bind the Docker
                socket. If True, the Docker socket is mounted. If False, it is
                removed.
            dev_container_config (DevContainer): The development container
                configuration object to update.
            tag (str): The tag for the container image. Defaults to 'latest'.
        """
        self._dev_container_config.name = (
            name or self._dev_container_config.name
        )
        self._dev_container_config.image = f'{image}:{tag}'
        if bind_docker_socket:
            self._dev_container_config.add_docker_mount()
        elif bind_docker_socket is False:
            self._dev_container_config.remove_docker_mount()

    def _get_dev_container_config_filename(self) -> Path:
        """Retrieves the absolute path to the dev container configuration file.

        This function creates the path to the `.devcontainer/devcontainer.json`
        file relative to the current working directory and resolves it to an
        absolute path.

        Returns:
            Path: The absolute path to the `devcontainer.json` file.
        """
        config_filename = (
            Path() / '.devcontainer/devcontainer.json'
        ).resolve()
        return config_filename

    def _get_existing_configuration(self) -> DevContainer:
        """Load an existing DevContainer configuration from a file.

        If the configuration file exists, it is loaded using the Loader class.
        If the file does not exist or is empty, a default DevContainer
        configuration is created using the project name from the provided
        Slough instance.

        Returns:
            DevContainer: The loaded or default DevContainer configuration.
        """
        return self._loader.load() or DevContainer(
            name=self._default_name, image=''
        )
