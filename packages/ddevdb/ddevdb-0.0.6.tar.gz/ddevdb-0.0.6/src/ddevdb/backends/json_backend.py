"""JSON backend module"""

import json
from typing import Any

from .base import BaseBackend


class JsonBackend(BaseBackend):
    """JSON Backend Class"""

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
                self.data = json.load(
                    fp=f,
                    object_hook=self.serializer_options.get("object_hook", None),
                    parse_float=self.serializer_options.get("parse_float", None),
                    parse_int=self.serializer_options.get("parse_int", None),
                    parse_constant=self.serializer_options.get("parse_constant", None),
                    object_pairs_hook=self.serializer_options.get(
                        "object_pairs_hook", None
                    ),
                )
        except (FileNotFoundError, EOFError):
            pass
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to load json file {self.filepath}: {e}") from e

    def save(self):
        """Save data in file"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(
                obj=self.data,
                fp=f,
                skipkeys=self.serializer_options.get("skipkeys", False),
                ensure_ascii=self.serializer_options.get("ensure_ascii", True),
                check_circular=self.serializer_options.get("check_circular", True),
                allow_nan=self.serializer_options.get("allow_nan", True),
                indent=self.serializer_options.get("indent", None),
                separators=self.serializer_options.get("separators"),
                default=self.serializer_options.get("default", None),
                sort_keys=self.serializer_options.get("sort_keys", False),
            )
