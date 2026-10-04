
def test_multiple_demands_category(project):
    """Verify adding and deleting multiple demand categories for a node."""
    project.init()
    
    # Add a junction
    j1 = project.addnode("J1", 0)
    
    # EPANET junctions created via API might already have 1 default demand.
    # Let's count initial demands.
    initial_demands = project.getnumdemands(j1)
    
    # Add 3 demand categories
    project.adddemand(j1, 1.0, "", "Cat1")
    project.adddemand(j1, 2.0, "", "Cat2")
    project.adddemand(j1, 3.0, "", "Cat3")
    
    # Check count
    num = project.getnumdemands(j1)
    assert num == initial_demands + 3
    
    # Base demands are 1-based.
    # New demands usually APPEND.
    assert project.getbasedemand(j1, initial_demands + 1) == 1.0
    assert project.getbasedemand(j1, initial_demands + 2) == 2.0
    assert project.getbasedemand(j1, initial_demands + 3) == 3.0
    
    # Delete the category we added (Cat2 at its index)
    target_idx = initial_demands + 2
    project.deletedemand(j1, target_idx)
    
    # Check count
    assert project.getnumdemands(j1) == initial_demands + 2
    
    # Verify that Cat3 shifted
    assert project.getbasedemand(j1, target_idx) == 3.0
