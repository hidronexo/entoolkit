import os

import pytest

from entoolkit import EPANETProject


@pytest.fixture
def net1_path():
    """Returns the absolute path to the Net1.inp sample network."""
    return os.path.join(os.path.dirname(__file__), "networks", "Net1.inp")

@pytest.fixture
def project():
    """Provides a fresh EPANETProject instance and ensures it is deleted after testing."""
    proj = EPANETProject()
    yield proj
    # Cleanup: close if open and delete
    try:
        proj.close()
    except:
        pass
    proj.delete()

@pytest.fixture
def relay_log_cleanup():
    """Fixture to cleanup test report files after each test."""
    yield
    for f in os.listdir("."):
        if f.endswith(".rpt") and f.startswith("test_"):
            try:
                os.remove(f)
            except:
                pass
