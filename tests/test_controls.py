from entoolkit import EN_CONTROLCOUNT, EN_LOWLEVEL, EN_PIPE, EN_TANK


def test_add_and_get_control(project):
    """Verify adding and retrieving simple controls."""
    project.init()
    
    # Create a small network
    j1 = project.addnode("J1", 0) # Junction
    t2 = project.addnode("T2", EN_TANK)
    p1 = project.addlink("P1", EN_PIPE, "J1", "T2")
    
    # Add a control: CLOSE P1 if tank T2 level is below 10.0
    # EN_addcontrol(ph, type, link, setting, node, level, *index)
    # setting: 0=CLOSED, 1=OPEN (for pipes)
    # type: EN_LOWLEVEL (0)
    ctl_idx = project.addcontrol(EN_LOWLEVEL, p1, 0.0, t2, 10.0)
    
    assert project.getcount(EN_CONTROLCOUNT) == 1
    
    # Retrieve and verify
    ctype, clink, cset, cnode, clev = project.getcontrol(ctl_idx)
    assert ctype == EN_LOWLEVEL
    assert clink == p1
    assert cset == 0.0
    assert cnode == t2
    assert abs(clev - 10.0) < 1e-6

def test_delete_control(project):
    """Verify deleting controls."""
    project.init()
    j1 = project.addnode("J1", 0)
    t2 = project.addnode("T2", EN_TANK)
    p1 = project.addlink("P1", EN_PIPE, "J1", "T2")
    
    idx1 = project.addcontrol(EN_LOWLEVEL, p1, 0.0, t2, 10.0)
    idx2 = project.addcontrol(EN_LOWLEVEL, p1, 1.0, t2, 20.0)
    assert project.getcount(EN_CONTROLCOUNT) == 2
    
    project.deletecontrol(idx1)
    assert project.getcount(EN_CONTROLCOUNT) == 1
