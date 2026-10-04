from entoolkit import (
    EN_DIAMETER,
    EN_ELEVATION,
    EN_HW,
    EN_JUNCTION,
    EN_LENGTH,
    EN_LPS,
    EN_PIPE,
    EN_RESERVOIR,
    EN_ROUGHNESS,
)


def test_build_network_from_scratch(project):
    """Verify that we can create nodes and links manually."""
    # Initialize a new empty project
    project.init(units=EN_LPS, hl=EN_HW)
    
    # Add nodes
    j1 = project.addnode("J1", EN_JUNCTION)
    j2 = project.addnode("J2", EN_JUNCTION)
    res = project.addnode("RES", EN_RESERVOIR)
    
    # Set properties
    project.setnodevalue(j1, EN_ELEVATION, 100.0)
    project.setnodevalue(res, EN_ELEVATION, 150.0)
    
    # Add links
    pipe = project.addlink("P1", EN_PIPE, "RES", "J1")
    
    # Verify properties
    assert project.getnodevalue(j1, EN_ELEVATION) == 100.0
    assert project.getcount(0) == 3 # Nodes
    assert project.getcount(1) == 1 # Links
    
    # Check link connectivity
    assert project.getlinkid(pipe) == "P1"
    
    # Run a simple check (won't solve fully without more data, but verify API calls)
    project.setlinkvalue(pipe, EN_DIAMETER, 200.0)
    project.setlinkvalue(pipe, EN_LENGTH, 500.0)
    project.setlinkvalue(pipe, EN_ROUGHNESS, 100.0)
    
    assert project.getlinkvalue(pipe, EN_DIAMETER) == 200.0
