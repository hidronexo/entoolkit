import importlib
import unittest.mock as mock


def test_platform_logic_isolated():
    """Test the OS and architecture detection branches in legacy.py in an isolated environment."""
    
    # We use a fresh import after patching
    # Since legacy might already be imported, we'll use a mocked version 
    # and importlib.reload but ONLY here.
    
    import entoolkit.legacy as legacy
    
    test_cases = [
        ("Linux", "x86_64"),
        ("Linux", "aarch64"),
        ("Darwin", "x86_64"),
        ("Darwin", "arm64"),
        # We don't need to test every single one if we hit the lines.
    ]
    
    for syst, mach in test_cases:
        with mock.patch("platform.system", return_value=syst), \
             mock.patch("platform.machine", return_value=mach), \
             mock.patch("ctypes.CDLL", return_value=mock.Mock()), \
             mock.patch("ctypes.WinDLL", return_value=mock.Mock()):
            
            # Reload inside the context
            importlib.reload(legacy)
            
            if syst == "Linux":
                assert "linux" in str(legacy._lib_path)
            elif syst == "Darwin":
                assert "darwin" in str(legacy._lib_path)

    # FINAL RELOAD to restore Windows state for other tests
    # No mocks here = real platform (Windows)
    importlib.reload(legacy)
