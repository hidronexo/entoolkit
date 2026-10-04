import pytest

from entoolkit import legacy


def test_modern_invalid_node_id(project, net1_path):
    project.open(net1_path)
    with pytest.raises(Exception) as excinfo:
        project.getnodeindex("NON_EXISTENT_NODE")
    assert "203" in str(excinfo.value) and "undefined node" in str(excinfo.value).lower()

def test_modern_invalid_property_value(project, net1_path):
    project.open(net1_path)
    idx = project.getnodeindex("10")
    # Setting an invalid property code should raise an error
    with pytest.raises(Exception):
        project.getnodevalue(idx, 9999)

def test_modern_file_not_found(project):
    with pytest.raises(Exception):
        project.open("non_existent_file.inp")

def test_legacy_error_codes(net1_path):
    # Legacy API should raise ENtoolkitError
    legacy.ENopen(net1_path, "", "")
    with pytest.raises(legacy.ENtoolkitError) as info:
        legacy.ENgetnodeindex("MISSING__NODE")
    assert info.value.ierr == 203
    assert "undefined node" in str(info.value).lower()
    legacy.ENclose()

def test_solver_without_open_project(project):
    with pytest.raises(Exception):
        project.solveH()
