"""Test configuration and fixtures"""
import os
import tempfile
from pathlib import Path

import pytest
from goldfish_backend.core.database import create_db_and_tables


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing"""
    # Create temporary database file
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_goldfish.db"

    # Set test database URL
    test_db_url = f"sqlite:///{db_path}"
    os.environ["GOLDFISH_DATABASE_URL"] = test_db_url

    # Create tables
    create_db_and_tables()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()
    os.rmdir(temp_dir)

    # Reset environment
    if "GOLDFISH_DATABASE_URL" in os.environ:
        del os.environ["GOLDFISH_DATABASE_URL"]


@pytest.fixture(scope="function")
def cli_runner():
    """Create a CLI test runner"""
    from click.testing import CliRunner
    return CliRunner()
