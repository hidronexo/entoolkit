import unittest.mock as mock

import pytest

from entoolkit import toolkit
from entoolkit.constants import *
from entoolkit.legacy import ENtoolkitError


def test_toolkit_full_mock_coverage_v2():
    """Systematically hit every branch in toolkit.py using mocks."""
    
    # Create a mock for the library
    mock_lib = mock.MagicMock()
    
    # ENSURE ALL ATTRIBUTE ACCESS RETURNS A MOCK THAT RETURNS 0
    def mock_ret_zero(*args, **kwargs): return 0
    mock_lib.EN_createproject.side_effect = mock_ret_zero
    mock_lib.EN_init.side_effect = mock_ret_zero
    mock_lib.EN_open.side_effect = mock_ret_zero
    mock_lib.EN_close.side_effect = mock_ret_zero
    mock_lib.EN_solveH.side_effect = mock_ret_zero
    mock_lib.EN_solveQ.side_effect = mock_ret_zero
    mock_lib.EN_deleteproject.side_effect = mock_ret_zero
    mock_lib.EN_geterror.side_effect = mock_ret_zero
    mock_lib.EN_setnodevalue.side_effect = mock_ret_zero
    mock_lib.EN_setlinkvalue.side_effect = mock_ret_zero
    mock_lib.EN_setpattern.side_effect = mock_ret_zero
    mock_lib.EN_setcontrol.side_effect = mock_ret_zero
    mock_lib.EN_deletecontrol.side_effect = mock_ret_zero
    mock_lib.EN_setoption.side_effect = mock_ret_zero
    mock_lib.EN_settitle.side_effect = mock_ret_zero
    mock_lib.EN_setdemandmodel.side_effect = mock_ret_zero
    mock_lib.EN_setbasedemand.side_effect = mock_ret_zero
    mock_lib.EN_adddemand.side_effect = mock_ret_zero
    mock_lib.EN_deletedemand.side_effect = mock_ret_zero
    mock_lib.EN_setqualtype.side_effect = mock_ret_zero

    with mock.patch("entoolkit.toolkit._lib", mock_lib):
        project = toolkit.EPANETProject()
        
        def mock_ptr_setter(val):
            def side_effect(*args):
                for arg in args:
                    if hasattr(arg, 'contents'):
                        arg.contents.value = val
                return 0
            return side_effect

        mock_lib.EN_getnodeindex.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getnodeid.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getnodevalue.side_effect = mock_ptr_setter(10.5)
        mock_lib.EN_getlinkindex.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getlinkid.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getlinkvalue.side_effect = mock_ptr_setter(10.5)
        mock_lib.EN_getcount.side_effect = mock_ptr_setter(5)
        mock_lib.EN_getnumdemands.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getbasedemand.side_effect = mock_ptr_setter(1.0)
        mock_lib.EN_getpatternindex.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getpatternvalue.side_effect = mock_ptr_setter(1.0)
        mock_lib.EN_getcontrol.side_effect = mock_ptr_setter(1)
        mock_lib.EN_getstatistic.side_effect = mock_ptr_setter(1.0)
        mock_lib.EN_getoption.side_effect = mock_ptr_setter(1.0)
        mock_lib.EN_addnode.side_effect = mock_ptr_setter(6)
        mock_lib.EN_addlink.side_effect = mock_ptr_setter(6)
        mock_lib.EN_addpattern.side_effect = mock_ptr_setter(2)
        mock_lib.EN_addcontrol.side_effect = mock_ptr_setter(2)
        
        # Success calls
        project.init()
        project.open("f")
        project.solveH()
        project.getnodeindex("N")
        project.getnodeid(1)
        project.getnodevalue(1, 0)
        project.setnodevalue(1, 0, 1.0)
        project.getnodevalues(0)
        project.addnode("N", 0)
        project.addlink("L", 0, "n1", "n2")
        
        # Fallback branches
        mock_lib.EN_addlink.side_effect = mock_ptr_setter(0)
        project.addlink("L2", 0, "n1", "n2")
        
        project.getlinkindex("L")
        project.getlinkid(1)
        project.getlinkvalue(1, 0)
        project.setlinkvalue(1, 0, 1.0)
        project.getlinkvalues(0)
        project.getcount(0)
        project.setdemandmodel(0,0,0,0)
        project.getnumdemands(1)
        project.getbasedemand(1,1)
        project.setbasedemand(1,1,1.0)
        project.adddemand(1, 1.0)
        project.deletedemand(1,1)
        project.setqualtype(0)
        project.solveQ()
        project.addpattern("P")
        
        mock_lib.EN_addpattern.side_effect = mock_ptr_setter(0)
        project.addpattern("P2")
        
        project.setpattern(1, [1.0])
        project.getpatternvalue(1, 1)
        project.addcontrol(0, 1, 1, 1, 1)
        project.getcontrol(1)
        project.setcontrol(1,0,1,1,1,1)
        project.deletecontrol(1)
        project.getstatistic(0)
        project.getoption(0)
        project.setoption(0, 1.0)
        
        # Title logic
        def mock_title_setter(p1, p2, p3):
            def side_effect(ph, b1, b2, b3):
                b1.value = b"T1"
                b2.value = b"T2"
                b3.value = b"T3"
                return 0
            return side_effect
        mock_lib.EN_gettitle.side_effect = mock_title_setter("a","b","c")
        project.gettitle()
        project.settitle("a")
        
        project.close()
        project.delete()
        project.delete() # Re-call check

        # Error branches
        mock_lib.EN_createproject.side_effect = lambda ph: 105
        with pytest.raises(ENtoolkitError):
            toolkit.EPANETProject()

def test_toolkit_del_v2():
    p = toolkit.EPANETProject()
    p.__del__()
