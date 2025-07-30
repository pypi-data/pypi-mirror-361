import shutil
import tempfile

import pytest


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment"""
    # Prevent tests from interfering with real user data
    monkeypatch.setenv("HOME", "/tmp/test_home")
    monkeypatch.setenv("USERPROFILE", "/tmp/test_home")
