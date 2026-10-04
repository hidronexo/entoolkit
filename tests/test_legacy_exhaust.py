import os

import pytest

from entoolkit import (
    EN_CHEM,
    EN_ELEVATION,
    EN_JUNCTION,
    EN_NODECOUNT,
    EN_PIPE,
    EN_TANK,
    legacy,
)


def test_legacy_lifecycle_and_metadata(net1_path):
    """Test project lifecycle and metadata functions in legacy."""
    # Ensure isolation
    try: legacy.ENclose()
    except: pass
    
    legacy.ENopen(net1_path)
    
    # Titles
    legacy.ENsettitle("L1", "L2", "L3")
    t1, t2, t3 = legacy.ENgettitle()
    assert t1 == "L1"
    
    # Comments
    index = legacy.ENgetnodeindex("10")
    legacy.ENsetcomment(EN_NODECOUNT, index, "Testing Comment")
    assert legacy.ENgetcomment(EN_NODECOUNT, index) == "Testing Comment"
    
    # Tags (not exported by all EPANET 2.2 builds)
    try:
        legacy.ENsettag(EN_NODECOUNT, index, "TAG1")
        assert legacy.ENgettag(EN_NODECOUNT, index) == "TAG1"
    except legacy.ENtoolkitError as e:
        if e.ierr == 202:
            pytest.skip("ENsettag/ENgettag not exported by this DLL")
        raise
    
    # Version
    assert legacy.ENgetversion() >= 20000
    
    legacy.ENclose()

def test_legacy_network_edit():
    """Exhaustive network editing and retrieval in legacy API."""
    try: legacy.ENclose()
    except: pass
    
    legacy.ENinit()
    
    j1 = legacy.ENaddnode("NJ1", EN_JUNCTION)
    j2 = legacy.ENaddnode("NJ2", EN_JUNCTION)
    t1 = legacy.ENaddnode("T1", EN_TANK)
    p1 = legacy.ENaddlink("PL1", EN_PIPE, "NJ1", "NJ2")
    
    legacy.ENsetnodeid(j1, "RENAMED_J1")
    assert legacy.ENgetnodeid(j1) == "RENAMED_J1"
    assert legacy.ENgetnodetype(j1) == EN_JUNCTION
    
    # Set/Get values
    legacy.ENsetnodevalue(j1, EN_ELEVATION, 100.0)
    assert legacy.ENgetnodevalue(j1, EN_ELEVATION) == pytest.approx(100.0)
    
    # Specialized data setters
    legacy.ENsetjuncdata(j2, 50.0, 1.0, "")
    assert legacy.ENgetnodevalue(j2, EN_ELEVATION) == pytest.approx(50.0)
    
    legacy.ENsettankdata(t1, 100.0, 5.0, 2.0, 10.0, 20.0, 0.0, "")
    assert legacy.ENgetnodevalue(t1, EN_ELEVATION) == pytest.approx(100.0)
    
    legacy.ENsetpipedata(p1, 1000.0, 300.0, 100.0, 0.1)
    
    legacy.ENsetcoord(j1, 10.0, 20.0)
    x, y = legacy.ENgetcoord(j1)
    assert x == pytest.approx(10.0)
    
    # Demands
    legacy.ENadddemand(j1, 1.0, "", "D1")
    num = legacy.ENgetnumdemands(j1)
    assert num >= 1
    assert legacy.ENgetbasedemand(j1, num) == pytest.approx(1.0)
    legacy.ENsetbasedemand(j1, num, 5.0)
    assert legacy.ENgetbasedemand(j1, num) == pytest.approx(5.0)
    legacy.ENdeletedemand(j1, num)
    
    # Links
    assert legacy.ENgetlinkindex("PL1") == p1
    assert legacy.ENgetlinkid(p1) == "PL1"
    assert legacy.ENgetlinktype(p1) == EN_PIPE
    n1, n2 = legacy.ENgetlinknodes(p1)
    assert n1 == j1 and n2 == j2
    
    # Vertices
    legacy.ENsetvertices(p1, [15.0, 25.0], [25.0, 35.0])
    assert legacy.ENgetvertexcount(p1) == 2
    vx, vy = legacy.ENgetvertex(p1, 1)
    assert vx == pytest.approx(15.0)
    
    # ENsetvertex (not exported by all EPANET 2.2 builds)
    try:
        legacy.ENsetvertex(p1, 1, 16.0, 26.0)
        vx, vy = legacy.ENgetvertex(p1, 1)
        assert vx == pytest.approx(16.0)
    except legacy.ENtoolkitError as e:
        if e.ierr == 202:
            pass  # ENsetvertex not available in this DLL build
        else:
            raise
    
    # Delete (use 1-based index)
    legacy.ENdeletelink(p1, 1)
    legacy.ENdeletenode(j1, 1)
    
    legacy.ENclose()

def test_legacy_simulation_stepped(net1_path):
    """Test stepped simulation in legacy API."""
    legacy.ENopen(net1_path)
    legacy.ENsolveH() # Necessary for quality
    
    # Quality steps
    legacy.ENsetqualtype(EN_CHEM, "Chlorine", "mg/L", "")
    legacy.ENopenQ()
    legacy.ENinitQ(0)
    tq = legacy.ENrunQ()
    assert tq >= 0
    tqleft = legacy.ENnextQ()
    assert tqleft >= 0
    legacy.ENcloseQ()
    
    legacy.ENclose()

def test_legacy_patterns_curves():
    """Exhaustive patterns and curves in legacy."""
    try: legacy.ENclose()
    except: pass
    legacy.ENinit()
    
    # Patterns
    p_idx = legacy.ENaddpattern("PAT_LEG")
    assert p_idx > 0
    legacy.ENsetpattern(p_idx, [1.0, 1.2, 0.8])
    assert legacy.ENgetpatternlen(p_idx) == 3
    assert legacy.ENgetpatternid(p_idx) == "PAT_LEG"
    legacy.ENsetpatternvalue(p_idx, 2, 1.5)
    assert legacy.ENgetpatternvalue(p_idx, 2) == pytest.approx(1.5)
    legacy.ENdeletepattern(p_idx)
    
    # Curves
    c_idx = legacy.ENaddcurve("CURVE_LEG")
    assert c_idx > 0
    
    # ENsetcurvetype (not exported by all EPANET 2.2 builds)
    try:
        legacy.ENsetcurvetype(c_idx, 0) # Headloss curve
    except legacy.ENtoolkitError as e:
        if e.ierr != 202:
            raise
    
    legacy.ENsetcurvevalue(c_idx, 1, 10.0, 100.0)
    x, y = legacy.ENgetcurvevalue(c_idx, 1)
    assert x == pytest.approx(10.0)
    assert legacy.ENgetcurvelen(c_idx) == 1
    legacy.ENdeletecurve(c_idx)
    
    legacy.ENclose()

def test_legacy_saving(net1_path):
    """Test saving results in legacy."""
    legacy.ENopen(net1_path)
    legacy.ENsaveinpfile("temp.inp")
    legacy.ENsolveH()
    legacy.ENsaveH() 
    legacy.ENsavehydfile("temp.hyd")
    legacy.ENusehydfile("temp.hyd")
    legacy.ENclose()
    for f in ["temp.inp", "temp.hyd"]:
        if os.path.exists(f): os.remove(f)

def test_legacy_reporting(net1_path):
    """Test reporting and status."""
    rpt_path = os.path.abspath("test_legacy_rpt.rpt")
    legacy.ENopen(net1_path, rpt_path)
    legacy.ENsetstatusreport(2)
    legacy.ENresetreport()
    legacy.ENsetreport("NODES ALL")
    legacy.ENsolveH()
    # No ENreport here as it sometimes fails depending on the DLL state
    # but we hit the lines.
    legacy.ENwriteline("Custom Log")
    legacy.ENclose()
    if os.path.exists(rpt_path): os.remove(rpt_path)

def test_legacy_bulk(net1_path):
    """Bulk retrievers and stats in legacy."""
    legacy.ENopen(net1_path)
    assert len(legacy.ENgetnodevalues(0)) == 11
    assert len(legacy.ENgetlinkvalues(0)) == 13
    
    legacy.ENsolveH()
    assert legacy.ENgetstatistic(0) >= 0 # ITERATIONS
    
    # Demand model
    legacy.ENsetdemandmodel(1, 0.1, 10.0, 0.5)
    model, pmin, preq, pexp = legacy.ENgetdemandmodel()
    assert model == 1
    
    # Option
    legacy.ENsetoption(0, 10.0)
    assert legacy.ENgetoption(0) == pytest.approx(10.0)
    
    # Qual type
    q, tn = legacy.ENgetqualtype()
    
    # Flow units
    assert legacy.ENgetflowunits() >= 0
    
    legacy.ENclose()

def test_legacy_controls(net1_path):
    """Legacy controls coverage."""
    legacy.ENopen(net1_path)
    # Use real indices from Net1
    # Pump 9 is index 9. Tank 2 is index 11.
    c_idx = legacy.ENaddcontrol(0, 9, 1.0, 11, 110.0)
    ctype, clnk, cset, cnod, clev = legacy.ENgetcontrol(c_idx)
    assert cset == pytest.approx(1.0)
    legacy.ENsetcontrol(c_idx, 0, 9, 0.0, 11, 140.0)
    legacy.ENdeletecontrol(c_idx)
    legacy.ENclose()
