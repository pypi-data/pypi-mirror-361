"""Module with a ConfigFileFinder."""

from pathlib import Path


class ConfigFileFinder:
    """Class to find a config file."""

    def __init__(
        self,
        filename: str,
        max_directory_depth: int = 6,
        working_dir: Path = Path(),
    ) -> None:
        """Initialize the ConfigFileFinder.

        Args:
            filename (str, optional): The name of the configuration file.
                Should be with extension.
            max_directory_depth (int, optional): The maximum directory depth to
                search for the configuration file. Defaults to 6.
            working_dir (Path, optional): The working directory to start the
                search. Defaults to Path().
        """
        self._working_dir = working_dir
        self._max_directory_depth = max_directory_depth
        self._filename = filename

    def _file_exists_in_dir(self, dir: Path) -> Path | None:
        """Check if the configuration file exists in the directory.

        Args:
            dir (Path): The directory to check.
        """
        path = dir / self._filename
        if path.is_file():
            return path
        return None

    def find(self) -> Path | None:
        """Find the configuration file.

        Returns:
            Path | None: The configuration file path if found, None otherwise.
        """
        dir = self._working_dir.resolve()
        for _ in range(self._max_directory_depth):
            if self._file_exists_in_dir(dir):
                return dir / self._filename
            dir = dir.parent.resolve()
        return None
