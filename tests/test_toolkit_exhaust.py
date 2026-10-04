import ctypes
import unittest.mock as mock


def test_toolkit_getnodeid(project, net1_path):
    """Cover getnodeid lines."""
    project.open(net1_path)
    # Node 1 is node "10"
    assert project.getnodeid(1) == "10"

def test_toolkit_addlink_fallback(project):
    """Cover addlink index fallback logic (line 324)."""
    project.init()
    project.addnode("J1", 0)
    project.addnode("J2", 0)
    
    ADD_LNK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))
    GET_LNK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))

    def mock_addlink_func(ph, id, type, n1, n2, idx_ptr):
        idx_ptr.contents.value = 0 # Simulate failure to set index
        return 0
        
    def mock_getindex_func(ph, id, idx_ptr):
        idx_ptr.contents.value = 1
        return 0
    
    with mock.patch("entoolkit.toolkit._lib.EN_addlink", new=ADD_LNK_TYPE(mock_addlink_func)), \
         mock.patch("entoolkit.toolkit._lib.EN_getlinkindex", new=GET_LNK_TYPE(mock_getindex_func)):
        idx = project.addlink("L1", 0, "J1", "J2")
        assert idx == 1

def test_toolkit_bulk_retrievers(project, net1_path):
    """Cover getnodevalues and getlinkvalues."""
    project.open(net1_path)
    # Line 289
    ns = project.getnodevalues(0)
    assert len(ns) == 11
    # Line 388-389
    ls = project.getlinkvalues(0)
    assert len(ls) == 13

def test_toolkit_setbasedemand(project):
    """Cover setbasedemand (line 455)."""
    project.init()
    j1 = project.addnode("J1", 0)
    project.adddemand(j1, 1.0)
    # Junctions often had 1 demand, so we added a 2nd.
    idx = project.getnumdemands(j1)
    project.setbasedemand(j1, idx, 5.0)
    assert project.getbasedemand(j1, idx) == 5.0

def test_toolkit_setcontrol(project):
    """Cover setcontrol (line 578)."""
    project.init()
    j1 = project.addnode("J1", 0)
    t2 = project.addnode("T2", 2)
    p1 = project.addlink("P1", 1, "J1", "T2")
    c1 = project.addcontrol(0, p1, 1.0, t2, 10.0)
    project.setcontrol(c1, 0, p1, 0.0, t2, 5.0)
    ctype, clink, cset, cnode, clev = project.getcontrol(c1)
    assert cset == 0.0
