"""Base stuff"""

from pathlib import Path
from typing import Any


class BaseBackend:
    """Base backend class"""

    def __init__(
        self,
        filepath: Path,
        mode: str = "rw",
        serializer_options: dict | None = None,
        initial_data: dict | None = None,
    ):
        self.filepath = filepath
        self.mode = mode
        self.serializer_options = serializer_options or {}
        self.data = None

        # Load or initialize data depending on mode and file existence
        if self.filepath.exists():
            if "r" in self.mode:
                # Ignore initial_data and load from file
                self.load()
            elif "w" in self.mode:
                # Overwrite file if mode includes write only
                self.data = initial_data or self.default_data()
                self.save()
        else:
            # File does not exist
            if initial_data is not None:
                self.data = initial_data
                if "w" in self.mode:
                    self.save()
            else:
                # Start with empty data
                self.data = self.default_data()

    def default_data(self) -> Any:
        """Create empty data structure"""
        raise NotImplementedError(
            "Method 'create_empty_data' not implemented."
        )

    def insert(self, key: Any, value: Any):
        """Insert data. If key already exists, raise error"""
        raise NotImplementedError(
            "Method 'insert' not implemented."
        )

    def update(self, key: Any, value: Any):
        """Update data by key. If key does not exist, raise error"""
        self.insert(key=key, value=value)

    def get(self, key: Any = None) -> Any:
        """Get data by key"""
        raise NotImplementedError(
            "Method 'get' not implemented."
        )

    def delete(self, key: Any):
        """Delete data by key"""
        raise NotImplementedError(
            "Method 'delete' not implemented."
        )

    def exists(self, key: Any) -> bool:
        """Check if key exists"""
        raise NotImplementedError(
            "Method 'exists' not implemented."
        )

    def keys(self) -> list[Any]:
        """Get all keys"""
        raise NotImplementedError(
            "Method 'keys' not implemented."
        )

    def values(self) -> list[Any]:
        """Get all values"""
        raise NotImplementedError(
            "Method 'values' not implemented."
        )

    def items(self) -> list[tuple[Any, Any]]:
        """Get all items as (key, value) pairs"""
        raise NotImplementedError(
            "Method 'items' not implemented."
        )

    # Utilities
    def load(self):
        """Load file"""
        raise NotImplementedError(
            "Method 'load' not implemented."
        )

    def save(self):
        """Save data in file"""
        raise NotImplementedError(
            "Method 'save' not implemented."
        )
