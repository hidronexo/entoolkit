import ctypes
import unittest.mock as mock

import pytest

from entoolkit import EPANETProject


def test_project_creation_failure():
    """Cover line 163 in toolkit.py (EN_createproject failure)."""
    # ENtoolkitError's string is the error message from ENgeterror
    with mock.patch("entoolkit.toolkit._lib.EN_createproject", return_value=200), \
         mock.patch("entoolkit.legacy.ENgeterror", return_value="Mocked Error 200"):
        from entoolkit.legacy import ENtoolkitError
        with pytest.raises(ENtoolkitError) as exc:
            p = EPANETProject()
        assert "Mocked Error 200" in str(exc.value)

def test_toolkit_addpattern_fallback(project):
    """Cover addpattern index fallback logic (line 512)."""
    project.init()
    
    # We use CFUNCTYPE to create a real C-compatible function that ctypes can use
    # and that correctly handles the pointer argument.
    ADD_PAT_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))
    GET_PAT_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))

    def mock_addpattern_func(ph, pat_id, idx_ptr):
        idx_ptr.contents.value = 0
        return 0
        
    def mock_getindex_func(ph, pat_id, idx_ptr):
        idx_ptr.contents.value = 1
        return 0
    
    with mock.patch("entoolkit.toolkit._lib.EN_addpattern", new=ADD_PAT_TYPE(mock_addpattern_func)), \
         mock.patch("entoolkit.toolkit._lib.EN_getpatternindex", new=GET_PAT_TYPE(mock_getindex_func)):
        idx = project.addpattern("PAT1")
        assert idx == 1
