from entoolkit import EN_AGE, EN_DEMAND, EN_PDA, EN_QUALITY


def test_pda_simulation(project, net1_path):
    """Verify that shifting to PDA mode works."""
    project.open(net1_path)
    
    # Run in DDA mode first (default)
    project.solveH()
    dem_dda = project.getnodevalue(project.getnodeindex("10"), EN_DEMAND)
    
    # Change to PDA
    project.setdemandmodel(EN_PDA, 0.1, 20.0, 0.5)
    
    project.solveH()
    dem_pda = project.getnodevalue(project.getnodeindex("10"), EN_DEMAND)
    
    assert dem_pda <= dem_dda

def test_water_age_quality(project, net1_path):
    """Verify water age simulation."""
    project.open(net1_path)
    
    # Setup Age simulation
    project.setqualtype(EN_AGE)
    
    # Solve 
    project.solveH()
    project.solveQ()
    
    # Check age at a junction
    idx = project.getnodeindex("12")
    age = project.getnodevalue(idx, EN_QUALITY)
    assert age >= 0
