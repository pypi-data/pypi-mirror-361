"""Pickle backend module"""

import pickle
from typing import Any

from .base import BaseBackend


class PickleBackend(BaseBackend):
    """Picke backend class"""

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
        if "r" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow reading."
            )
        try:
            with open(self.filepath, "rb") as f:
                self.data = pickle.load(
                    file=f,
                    fix_imports=self.serializer_options.get("fix_imports", True),
                    encoding=self.serializer_options.get("encoding", "ASCII"),
                    errors=self.serializer_options.get("errors", "strict"),
                    buffers=self.serializer_options.get("buffers", ()),
                )
        except (FileNotFoundError, EOFError):
            pass
        except pickle.UnpicklingError as e:
            raise RuntimeError(
                f"Failed to load pickle file {self.filepath}: {e}"
            ) from e

    def save(self):
        """Save data in file"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        with open(self.filepath, "wb") as f:
            pickle.dump(
                obj=self.data,
                file=f,
                protocol=self.serializer_options.get(
                    "protocol", pickle.DEFAULT_PROTOCOL
                ),
                fix_imports=self.serializer_options.get("fix_imports", True),
                buffer_callback=self.serializer_options.get("buffer_callback", None),
            )
