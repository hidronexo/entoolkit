from entoolkit import EN_BASEDEMAND, EN_HW, EN_JUNCTION, EN_LPS, EN_PRESSURE


def test_project_simulation(project, net1_path):
    project.open(net1_path, "test_project.rpt", "")
    project.solveH()
    
    idx = project.getnodeindex("10")
    pressure = project.getnodevalue(idx, EN_PRESSURE)
    assert pressure > 0

def test_project_precision(project):
    """Test double precision in handle-based API."""
    project.init("", "", EN_LPS, EN_HW)
    
    idx = project.addnode("PREC_NODE", EN_JUNCTION)
    # High precision value
    test_val = 1.23456789012345
    project.setnodevalue(idx, EN_BASEDEMAND, test_val)
    
    ret_val = project.getnodevalue(idx, EN_BASEDEMAND)
    assert abs(test_val - ret_val) < 1e-12

def test_project_array_values(project, net1_path):
    """Test efficient array retrieval."""
    project.open(net1_path)
    
    pressures = project.getnodevalues(EN_PRESSURE)
    assert len(pressures) == project.getcount(0) # EN_NODECOUNT
    assert all(isinstance(v, float) for v in pressures)
