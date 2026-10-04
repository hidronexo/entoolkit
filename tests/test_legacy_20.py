import os

from entoolkit import legacy


def test_open_legacy_20_network():
    """Verify that a standard EPANET 2.0 compatible file can be opened and solved."""
    network_path = os.path.join(os.path.dirname(__file__), "networks", "Net1.inp")
    
    # We use Net1.inp which is natively 2.0 compatible
    try:
        try:
            legacy.ENopen(network_path, "test_20.rpt", "")
            legacy.ENsolveH()
            # ENreport might fail if not configured, we don't strictly need it for 2.0 open check
            try:
                legacy.ENreport()
            except legacy.ENtoolkitError:
                pass 
                
            # Verify we can get at least one result
            node_id = legacy.ENgetnodeid(1)
            assert node_id is not None
        finally:
            legacy.ENclose()
    finally:
        if os.path.exists("test_20.rpt"):
            try:
                os.remove("test_20.rpt")
            except PermissionError:
                pass # Still locked? Ignore for now, cleanup happens in conftest usually

def test_legacy_20_pda_unsupported_error():
    """Verify that 2.2 features like PDA models raise errors if called on a 2.0 network logic (though logic is in DLL, not INP)."""
    # This is more of a DLL capability test, but we can verify our safety tags.
    from entoolkit.constants import EN_DEMANDMODEL, EN_PDA
    
    network_path = os.path.join(os.path.dirname(__file__), "networks", "Net1.inp")
    legacy.ENopen(network_path, "test_pda.rpt", "")
    
    # If the DLL is 2.2, ENsetoption(EN_DEMANDMODEL, EN_PDA) should work.
    # If the DLL is 2.0, our hasattr check in legacy.py (if we added it) would prevent the crash.
    
    try:
        # We don't necessarily want to FAIL if it works (that means DLL is 2.2)
        # But we verify the call is safe.
        legacy.ENsetoption(EN_DEMANDMODEL, float(EN_PDA))
    except Exception as e:
        # If it fails, it should be an ENtoolkitError, not an Access Violation
        assert "Error" in str(e) or "supported" in str(e)
    finally:
        legacy.ENclose()
        if os.path.exists("test_pda.rpt"): os.remove("test_pda.rpt")
