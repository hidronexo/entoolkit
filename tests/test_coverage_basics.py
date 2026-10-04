import unittest.mock as mock

import entoolkit.legacy as legacy
from entoolkit.logger import init_logger


def test_logger_reinit():
    """Cover the branch where logger is already initialized."""
    l1 = init_logger()
    l2 = init_logger()
    assert l1 is l2

def test_undocumented_error():
    """Trigger the branch in ENtoolkitError for undocumented errors."""
    with mock.patch("entoolkit.legacy.ENgeterror", side_effect=Exception("Failed")):
        err = legacy.ENtoolkitError(9999)
        assert "Toolkit Error 9999" in str(err)

def test_nontype_error():
    """Trigger the branch in ENtoolkitError for non-convertible error codes."""
    err = legacy.ENtoolkitError("NONE") # Non-int
    assert err.warning is False
    assert "Toolkit Error NONE" in str(err)

def test_toolkit_warning():
    """Trigger the warning branch (ierr < 100)."""
    with mock.patch("entoolkit.legacy.ENgeterror", return_value="Warn"):
        err = legacy.ENtoolkitError(5)
        assert err.warning is True
        assert "Warn" in str(err)
