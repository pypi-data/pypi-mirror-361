"""Module with a StorageManager for YAML files."""

from pathlib import Path

import yaml

from slough.exceptions import ConfigNotLoadedError
from slough_config import DevelopmentEnvironment, SloughConfig

from .storage_manager import StorageManager


def development_environment_representer(
    dumper: yaml.Dumper, data: DevelopmentEnvironment
) -> yaml.ScalarNode:
    """Custom YAML representer for the DevelopmentEnvironment class.

    This function defines how instances of the DevelopmentEnvironment class
    should be represented when dumping to a YAML file. It converts the
    DevelopmentEnvironment instance to a YAML scalar with the appropriate tag.

    Args:
        dumper (yaml.Dumper): The YAML dumper instance.
        data (DevelopmentEnvironment): The DevelopmentEnvironment instance to
            be represented.

    Returns:
        yaml.ScalarNode: The YAML node representing the DevelopmentEnvironment
            instance.
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.value)


yaml.add_representer(
    DevelopmentEnvironment, development_environment_representer
)


class YAMLStorageManager(StorageManager):
    """StorageManager for YAML files."""

    def __init__(self, file_path: Path) -> None:
        """Initialize the YAMLStorageManager.

        Args:
            file_path (Path): Path to the YAML file.
        """
        self.file_path = file_path

    def save(self, data: SloughConfig) -> None:
        """Save data to a YAML file.

        Args:
            data (SloughConfig): Data to save.
        """
        with open(self.file_path, 'w') as file:
            yaml.dump(data.model_dump(), file)

    def load(self) -> SloughConfig:
        """Load data from a YAML file.

        Returns:
            SloughConfig: Loaded data.
        """
        try:
            with open(self.file_path) as file:
                return SloughConfig(**yaml.load(file, Loader=yaml.FullLoader))
        except FileNotFoundError as exc:
            raise ConfigNotLoadedError(
                'Configuration file not found.'
            ) from exc
