"""Something"""

from .pickle_backend import PickleBackend
from .json_backend import JsonBackend
from.inmemory_backend import InMemoryBackend

_BACKENDS = {
    "pickle": PickleBackend,
    "json": JsonBackend,
    # "inmemory": InMemoryBackend,
}

_DEFAULTS = {
    "pickle": {
        "filename": "database.pkl",
    },
    "json": {
        "filename": "database.json"
    }
}


def get_backend(name: str):
    """Returns the backend class"""
    try:
        return _BACKENDS[name]
    except KeyError as e:
        raise ValueError(f"Unknown backend: {name}") from e

def get_backend_filename(backend_name: str) -> str:
    """Returns the default filename for specified backend"""
    try:
        return _DEFAULTS[backend_name]["filename"]
    except KeyError as e:
        raise ValueError(f"Unknown backend: {backend_name}") from e

def register_backend(name: str, backend_class):
    """Register a backend class.
    After registration it can be used as a backend.
    """
    if name in _BACKENDS:
        raise NameError(f"Backend '{name}' already exists.")

    _BACKENDS.update({name: backend_class})

def get_mandatory_settings(backend: str) -> dict:
    """If the backend class has mandatory settings
    this function returns them. Useful if a backend
    does not allow stuff like saving (so there can't
    be a filename or filepath)
    """
