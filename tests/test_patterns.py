from entoolkit import EN_PATCOUNT


def test_add_and_get_pattern(project):
    """Verify adding and retrieving time patterns."""
    project.init()
    
    # Add a pattern
    pat_name = "TEST_PAT"
    idx = project.addpattern(pat_name)
    
    # Check count
    assert project.getcount(EN_PATCOUNT) == 1
    
    # Set pattern values
    factors = [1.0, 1.2, 0.8, 1.5]
    project.setpattern(idx, factors)
    
    # Retrieving values
    # EPANET pattern periods are 1-based
    assert abs(project.getpatternvalue(idx, 1) - 1.0) < 1e-6
    assert abs(project.getpatternvalue(idx, 2) - 1.2) < 1e-6
    assert abs(project.getpatternvalue(idx, 3) - 0.8) < 1e-6
