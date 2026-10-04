import importlib
import unittest.mock as mock

import pytest


def test_platform_loading_coverage():
    """
    Force execution of platform-specific branches in legacy.py.
    This uses importlib.reload and extensive mocking of platform and ctypes.
    """
    
    # We need to mock several things before reloading the module
    with mock.patch("platform.system") as mock_system, \
         mock.patch("platform.machine") as mock_machine, \
         mock.patch("ctypes.WinDLL", create=True) as mock_windll, \
         mock.patch("ctypes.CDLL", create=True) as mock_cdll:
        
        # Ensure they return mock objects that can have attributes (for the initialization loop)
        mock_lib = mock.MagicMock()
        mock_windll.return_value = mock_lib
        mock_cdll.return_value = mock_lib
        
        # 1. Test Windows x86 (to hit the arch selection branch)
        mock_system.return_value = "Windows"
        mock_machine.return_value = "i386"
        from entoolkit import legacy
        importlib.reload(legacy)
        
        # 2. Test Mac (Darwin) ARM64
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"
        importlib.reload(legacy)
        
        # 3. Test Linux (default case) x64
        mock_system.return_value = "Linux"
        mock_machine.return_value = "x86_64"
        importlib.reload(legacy)

    # Reload one last time with REAL parameters or windows-safe ones to restore sanity
    importlib.reload(legacy)

def test_missing_library_error():
    """Test the failure case when the library cannot be loaded."""
    with mock.patch("platform.system", return_value="Windows"), \
         mock.patch("ctypes.WinDLL", side_effect=OSError("DLL not found")):
        from entoolkit import legacy
        with pytest.raises(OSError):
            importlib.reload(legacy)
    
    # Restore legacy module state
    importlib.reload(legacy)
