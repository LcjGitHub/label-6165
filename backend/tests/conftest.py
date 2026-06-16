import gc
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import db
from app import app
from seed import seed_if_empty


def _cleanup_test_db(db_path, original_db_path, original_db_dir):
    db.DB_PATH = original_db_path
    db.DB_DIR = original_db_dir
    gc.collect()
    try:
        if db_path.exists():
            db_path.unlink(missing_ok=True)
    except (PermissionError, OSError):
        pass


@pytest.fixture
def client():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_plants.db"

    original_db_path = db.DB_PATH
    original_db_dir = db.DB_DIR
    db.DB_PATH = db_path
    db.DB_DIR = db_path.parent

    try:
        db.init_db()

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client
    finally:
        _cleanup_test_db(db_path, original_db_path, original_db_dir)


@pytest.fixture
def client_with_seed():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_plants.db"

    original_db_path = db.DB_PATH
    original_db_dir = db.DB_DIR
    db.DB_PATH = db_path
    db.DB_DIR = db_path.parent

    try:
        db.init_db()
        seed_if_empty()

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client
    finally:
        _cleanup_test_db(db_path, original_db_path, original_db_dir)
