"""
Global pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture(scope="function")
def sample_data():
    """Sample data for testing."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "active": True
    }


@pytest.fixture(scope="function")
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("test content")
    return temp_file


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --runslow is given."""
    if config.getoption("--runslow"):
        return
    
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="run slow tests"
    )