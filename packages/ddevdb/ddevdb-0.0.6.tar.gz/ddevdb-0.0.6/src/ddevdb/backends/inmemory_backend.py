"""In memory backend"""

from pathlib import Path
from typing import Any

from .base import BaseBackend


class InMemoryBackend(BaseBackend):
    """JSON Backend Class"""

    def __init__(  # pylint: disable=super-init-not-called, unused-argument
        self,
        initial_data: dict | None = None,
        **kwargs,
    ):
        self.data = None

        if initial_data is not None:
            self.data = initial_data
        else:
            # Start with empty data
            self.data = self.default_data()

    def default_data(self) -> dict:
        return {}

    def insert(self, key: Any, value: Any):
        """Insert data. If key already exists, raise error"""
        self.data[key] = value

    def update(self, key: Any, value: Any):
        """Update data by key. If key does not exist, raise error"""
        self.insert(key=key, value=value)

    def get(self, key: Any = None) -> Any:
        """Get data by key"""
        if key is not None:
            return self.data[key]
        return self.data

    def delete(self, key: Any):
        """Delete data by key"""
        del self.data[key]

    def exists(self, key: Any) -> bool:
        """Check if key exists"""
        return key in self.data.keys()

    def keys(self) -> list[Any]:
        """Get all keys"""
        return self.data.keys()

    def values(self) -> list[Any]:
        """Get all values"""
        return self.data.values()

    def items(self) -> list[tuple[Any, Any]]:
        """Get all items as (key, value) pairs"""
        return self.data.items()

    # Utilities
    def load(self):
        """Load file"""
        raise PermissionError(f"'{self.__class__.__name__}' doesn't support loading")

    def save(self):
        """Save data in file"""
        raise PermissionError(f"'{self.__class__.__name__}' doesn't support saving")
