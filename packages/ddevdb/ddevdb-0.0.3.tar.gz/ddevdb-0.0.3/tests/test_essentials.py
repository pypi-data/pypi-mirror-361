"""Primary and most important tests"""

import tempfile
from pathlib import Path

import pytest

from ddevdb import Database


def test_essentials():
    """Test read and write"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "db.pkl"
        data = {"foo": "bar"}

        db = Database(filepath=db_path, mode="rw", initial_data=data)

        assert db.get() == data, "Initial data is not the same"

        db.insert("baz", 123)
        assert db.exists("baz"), "Insert not working properly"

        db.update("foo", 321)
        assert db.get("foo") == 321, "Update not working properly"


def test_pickle_backend_write_denied():
    """
    Test permission error when db is
    in read only mode and save is called
    """
    # TODO
    return
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "db.pkl"
        backend = PickleBackend(db_path, mode="r")

        with pytest.raises(PermissionError):
            backend.save()
