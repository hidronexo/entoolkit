from entoolkit import legacy as toolkit


def test_version():
    assert toolkit.ENgetversion() == 20200

def test_simulation(net1_path):
    # Run full simulation
    toolkit.ENopen(net1_path, "test_toolkit.rpt", "")
    toolkit.ENsolveH()
    
    # Check some values
    # Node 1 is a junction in Net1
    idx = toolkit.ENgetnodeindex("10")
    pressure = toolkit.ENgetnodevalue(idx, toolkit.EN_PRESSURE)
    assert pressure > 0
    
    toolkit.ENclose()

def test_demand_api():
    toolkit.ENinit("test_demand.rpt", "", toolkit.EN_LPS, toolkit.EN_HW)
    
    idx = toolkit.ENaddnode("D_TEST", toolkit.EN_JUNCTION)
    toolkit.ENadddemand(idx, 15.0, "", "Category_A")
    
    # Net1 node addition usually counts from 1 if empty
    num = toolkit.ENgetnumdemands(idx)
    # Default demand (0) + Category_A
    assert num >= 1
    
    toolkit.ENclose()
