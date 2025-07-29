"""Module with a Loader class for loading DevContainer configurations."""

from pathlib import Path

from pydantic import ValidationError

from .model import DevContainer


class Loader:
    """Class to load DevContainer configurations."""

    def __init__(self, path: Path) -> None:
        """Initialize the Loader class.

        Args:
            path (Path): The path to load the configuration file from.
        """
        self.path = path

    def load(self) -> DevContainer | None:
        """Load the DevContainer configuration from a file.

        Returns:
            Optional[DevContainer]: The loaded DevContainer instance or None if
            the file does not exist or is invalid.
        """
        try:
            with open(self.path) as file:
                return DevContainer.model_validate_json(file.read())
        except (ValidationError, FileNotFoundError):
            return None
