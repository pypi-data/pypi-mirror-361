"""Module with the StorageManager class."""

from abc import ABC, abstractmethod

from slough_config import SloughConfig


class StorageManager(ABC):
    """Abstract class for storage managers."""

    @abstractmethod
    def save(self, data: SloughConfig) -> None:
        """Save data to storage.

        Args:
            data (SloughConfig): Data to save.
        """

    @abstractmethod
    def load(self) -> SloughConfig:
        """Load data from storage.

        Returns:
            SloughConfig: Loaded data.
        """
