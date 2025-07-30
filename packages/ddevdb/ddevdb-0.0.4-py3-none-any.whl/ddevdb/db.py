"""
Something
"""

import os
from pathlib import Path
from threading import Lock
from typing import Any

from platformdirs import user_data_dir

from .backends import get_backend, get_backend_filename


class Database:
    """
    A simple database interface with pluggable backends.

    Parameters
    ----------
    filepath : str | Path | None
        Path to the database file. If None, a sensible default will be used.
    backend : str
        Which backend to use (e.g., 'pickle', 'json', and more to come). Default is 'pickle'.
    auto_save : bool
        If True, automatically saves to disk after every write operation. Default is True.
    mode : str
        Mode to open the database. E.g., 'rw', 'r', 'w'. Default is 'rw'.
    serializer_options : dict | None
        Optional backend-specific serialization options.
    initial_data : dict | None
        Initial data to populate the database with if file does not exist.
    lock : bool
        If True, enables a thread lock to prevent concurrent writes. Default is False.
    """

    _instances = {}

    def __new__(
        cls,
        *args,
        filename: str = None,
        filepath: str | Path | None = None,
        backend: str = None,
        auto_save: bool = None,
        mode: str = None,
        lock: bool = None,
        **kwargs,
    ):
        backend = backend if backend is not None else "pickle"
        auto_save = True if auto_save is None else auto_save
        mode = mode if mode is not None else "rw"
        lock = False if lock is None else lock

        key_items = [
            ("filename", filename),
            ("filepath", filepath),
            ("backend", backend),
            ("auto_save", auto_save),
            ("mode", mode),
            ("lock", lock),
        ]
        key = tuple(sorted(key_items))

        if key in cls._instances:
            return cls._instances[key]

        instance = super().__new__(cls)
        cls._instances[key] = instance
        return instance

    def __init__(
        self,
        filename: str = None,
        filepath: str | Path | None = None,
        backend: str = "pickle",
        auto_save: bool = True,
        mode: str = "rw",
        serializer_options: dict | None = None,
        initial_data: dict | None = None,
        lock: bool = False,
    ):
        # Resolve file path
        if filepath is None:
            default_dir = Path(user_data_dir("ddevdb"))
            default_dir.mkdir(parents=True, exist_ok=True)
            if filename is not None:
                filepath = default_dir / filename
            else:
                # No filename provided. Use default
                filepath = default_dir / get_backend_filename(backend_name=backend)
        else:
            # Check if filepath points to a directory
            if os.path.isdir(filepath):
                filepath = os.path.join(
                    filepath, get_backend_filename(backend_name=backend)
                )
            filepath = Path(filepath)

        self.filepath = filepath
        self.backend_name = backend
        self.auto_save = auto_save
        self.mode = mode
        self.serializer_options = serializer_options or {}
        self.initial_data = initial_data
        self.lock_enabled = lock
        self._lock = Lock() if lock else None

        # Create backend instance
        backend_cls = get_backend(self.backend_name)
        self._backend = backend_cls(
            self.filepath,
            mode=self.mode,
            serializer_options=self.serializer_options,
            initial_data=self.initial_data,
        )

        self.load(safe=True)

    def __setattr__(self, name, value):
        # TODO: Improve this. Some attributes should be able to
        # get changed after init.
        if not hasattr(self, name):
            # Allow setting values the first time, then block
            super().__setattr__(name, value)
        elif name in (
            "filepath",
            "backend_name",
            "_backend",
            "auto_save",
            "mode",
            "initial_data",
            "lock_enabled",
        ):
            raise AttributeError(
                f"Cannot modify attribute '{name}' after initialization."
            )

    # acquire/release helpers if lock is enabled
    def _acquire(self):
        if self._lock:
            self._lock.acquire()

    def _release(self):
        if self._lock:
            self._lock.release()

    # APIs
    def insert(self, key: Any, value: Any):
        """Insert data. If key already exists, raise error"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        if self.exists(key=key):
            raise KeyError(f"Key '{key}' already exists in the database.")
        try:
            self._acquire()
            self._backend.insert(key=key, value=value)
            if self.auto_save:
                self.save()
        finally:
            self._release()

    def update(self, key: Any, value: Any):
        """Update data by key. If key does not exist, raise error"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        if not self.exists(key=key):
            raise KeyError(f"Key '{key}' does not exist in the database.")
        try:
            self._acquire()
            self._backend.update(key=key, value=value)
            if self.auto_save:
                self.save()
        finally:
            self._release()

    def get(self, key: Any = None, default: Any = None, safe: bool = True) -> Any:
        """Get data by key"""
        if key is not None and not self.exists(key=key):
            if not safe and default is None:
                raise KeyError(f"Key '{key}' does not exist in the database.")
            if default is not None:
                return default
            return None
        return self._backend.get(key=key)

    def delete(self, key: Any):
        """Delete data by key"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        if not self.exists(key=key):
            raise KeyError(f"Key '{key}' does not exist in the database.")
        try:
            self._acquire()
            self._backend.delete(key=key)
            if self.auto_save:
                self.save()
        finally:
            self._release()

    def exists(self, key: Any) -> bool:
        """Check if key exists"""
        return self._backend.exists(key=key)

    def keys(self) -> list[Any]:
        """Get all keys"""
        return self._backend.keys()

    def values(self) -> list[Any]:
        """Get all values"""
        return self._backend.values()

    def items(self) -> list[tuple[Any, Any]]:
        """Get all items as (key, value) pairs"""
        return self._backend.items()

    # Utilities
    def clear(self):
        """Clear the database"""
        if "w" not in self.mode:
            raise PermissionError(
                f"Database opened in mode '{self.mode}' does not allow writing."
            )
        try:
            self._acquire()
            for k in self.keys():
                self.delete(key=k)
            if self.auto_save:
                self.save()
        finally:
            self._release()

    def save(self, safe: bool = False):
        """Save the database to disk"""
        if "w" not in self.mode:
            if not safe:
                raise PermissionError(
                    f"Database opened in mode '{self.mode}' does not allow writing."
                )
            return
        self._backend.save()

    def load(self, safe: bool = False):
        """Load the database from disk"""
        if "r" not in self.mode:
            if not safe:
                raise PermissionError(
                    f"Database opened in mode '{self.mode}' does not allow reading."
                )
            return
        self._backend.load()

    def __iter__(self):
        """Iterate over items"""
        return iter(self.items())

    def __getitem__(self, key: Any) -> Any:
        """Get item by key"""
        return self.get(key, safe=False)

    def __setitem__(self, key: Any, value: Any):
        """Set item by key"""
        self.insert(key, value)
        if self.auto_save:
            self.save()

    def __delitem__(self, key: Any):
        """Delete item by key"""
        self.delete(key)
        if self.auto_save:
            self.save()

    def __contains__(self, key: Any) -> bool:
        """Check if key exists"""
        return self.exists(key)

    def __len__(self) -> int:
        """Get number of items"""
        return len(self.keys())

    def __repr__(self) -> str:
        """String representation"""
        if self.backend_name and self.mode and self.filepath:
            return (
                f"<Database backend='{self.backend_name}' "
                f"mode='{self.mode}' filepath='{self.filepath}'>"
            )
        return f"<Database backend='{self.backend_name}' mode='{self.mode}'>"

    def __enter__(self):
        """Context manager enter"""
        if self.lock_enabled:
            self._acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit"""
        if self.lock_enabled:
            self._release()
        if exc_type is None:
            # Always save after exit
            self.save()
        return False
