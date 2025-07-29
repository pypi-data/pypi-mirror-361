"""Module with the DevContainer dataclass."""

from pydantic import BaseModel, Field


class DevContainer(BaseModel):
    """Dataclass representing a DevContainer configuration."""

    name: str
    image: str
    remote_environment: dict[str, str] = Field(
        default_factory=dict, alias='remoteEnv'
    )
    mounts: list[str] = []

    def add_docker_mount(self) -> None:
        """Add a Docker mount to the DevContainer configuration."""
        mount = (
            'source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind'
        )
        self.add_mount(mount)

    def remove_docker_mount(self) -> None:
        """Remove the Docker mount from the DevContainer configuration."""
        mount = (
            'source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind'
        )
        if mount in self.mounts:
            self.mounts.remove(mount)

    def add_mount(self, mount: str) -> None:
        """Add a mount to the DevContainer configuration.

        Args:
            mount (str): The mount to add.
        """
        if mount not in self.mounts:
            self.mounts.append(mount)

    def add_environment_variable(self, variable: str, value: str) -> None:
        """Add an environment variable to the DevContainer configuration.

        Args:
            variable (str): The name of the environment variable.
            value (str): The value of the environment variable.
        """
        self.remote_environment[variable] = value
