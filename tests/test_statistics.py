from entoolkit import (
    EN_CONTROLCOUNT,
    EN_CURVECOUNT,
    EN_ITERATIONS,
    EN_LINKCOUNT,
    EN_NODECOUNT,
    EN_PATCOUNT,
    EN_RELATIVEERROR,
    EN_RULECOUNT,
)


def test_simulation_statistics(project, net1_path):
    """Verify retrieval of hydraulic simulation statistics."""
    project.open(net1_path)
    project.solveH()
    
    iters = project.getstatistic(EN_ITERATIONS)
    rel_err = project.getstatistic(EN_RELATIVEERROR)
    
    assert iters >= 0
    assert rel_err >= 0
    # In a balanced simulation, relative error should be small
    assert rel_err < 1.0 

def test_network_counts_all(project, net1_path):
    """Verify counts for all object types in Net1."""
    project.open(net1_path)
    
    assert project.getcount(EN_NODECOUNT) == 11
    assert project.getcount(EN_LINKCOUNT) == 13
    assert project.getcount(EN_PATCOUNT) == 1
    assert project.getcount(EN_CURVECOUNT) == 1
    assert project.getcount(EN_CONTROLCOUNT) == 2
    assert project.getcount(EN_RULECOUNT) == 0
