from entoolkit import EN_ACCURACY, EN_FLOWUNITS, EN_TRIALS


def test_project_titles(project):
    """Verify setting and getting project titles."""
    project.init()
    t1, t2, t3 = "Line 1", "Line 2", "Line 3"
    project.settitle(t1, t2, t3)
    
    rt1, rt2, rt3 = project.gettitle()
    assert rt1 == t1
    assert rt2 == t2
    assert rt3 == t3

def test_project_options(project):
    """Verify setting and getting project options."""
    project.init()
    
    # Accuracy
    project.setoption(EN_ACCURACY, 0.005)
    assert abs(project.getoption(EN_ACCURACY) - 0.005) < 1e-6
    
    # Trials
    project.setoption(EN_TRIALS, 50)
    assert project.getoption(EN_TRIALS) == 50
    
    # Units (read-only in some versions via setoption, but let's check)
    # Usually units are set in EN_init, but EN_getoption can read them.
    val = project.getoption(EN_FLOWUNITS)
    assert val >= 0
