"""Module with a Saver class for saving DevContainer configurations."""

from pathlib import Path

from .model import DevContainer


class Saver:
    """Class to save DevContainer configurations."""

    def __init__(self, path: Path) -> None:
        """Initialize the Saver class.

        Args:
            path (Path): The path to save the configuration file.
        """
        self.path = path

    def save(self, dev_container: DevContainer) -> None:
        """Save the DevContainer configuration to a file.

        Args:
            dev_container (DevContainer): The DevContainer instance to save.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as file:
            file.write(
                dev_container.model_dump_json(
                    indent=4, by_alias=True, exclude_defaults=True
                )
            )
