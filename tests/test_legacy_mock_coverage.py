import unittest.mock as mock

import pytest

from entoolkit import legacy
from entoolkit.constants import *


def test_legacy_all_mocked_success():
    """Hit all functions with success (0) results."""
    def zero_func(*args, **kwargs): return 0
    class MockLib:
        def __getattr__(self, name): return mock.Mock(side_effect=zero_func)
    mock_lib = MockLib()
    
    with mock.patch("entoolkit.legacy._lib", mock_lib):
        def mock_ptr_setter(val):
            def side_effect(*args):
                for arg in args:
                    if hasattr(arg, 'contents'):
                        arg.contents.value = val
                return 0
            return side_effect

        def custom_getattr(name):
            if name.startswith("ENget"): return mock.Mock(side_effect=mock_ptr_setter(1))
            return mock.Mock(side_effect=zero_func)
        MockLib.__getattr__ = lambda self, name: custom_getattr(name)

        # Call everything
        legacy.ENinit("r", "b", 0)
        legacy.ENopen("i", "r", "b")
        legacy.ENgettitle()
        legacy.ENsettitle("a", "b", "c")
        legacy.ENgetcomment(1, 1)
        legacy.ENsetcomment(1, 1, "c")
        legacy.ENgettag(1, 1)
        legacy.ENsettag(1, 1, "t")
        legacy.ENgetnodeindex("N")
        legacy.ENgetnodeid(1)
        legacy.ENgetnodetype(1)
        legacy.ENgetnodevalue(1, 0)
        legacy.ENsetnodeid(1, "N2")
        legacy.ENsetnodevalue(1, 0, 1.0)
        legacy.ENaddnode("N3", 0)
        legacy.ENdeletenode(1, 0)
        legacy.ENgetlinkindex("L")
        legacy.ENgetlinkid(1)
        legacy.ENgetlinktype(1)
        legacy.ENgetlinknodes(1)
        legacy.ENgetlinkvalue(1, 0)
        legacy.ENsetlinkvalue(1, 0, 1.0)
        legacy.ENaddlink("L2", 0, "N1", "N2")
        legacy.ENdeletelink(1, 0)
        legacy.ENgetcount(0)
        legacy.ENgetflowunits()
        legacy.ENgettimeparam(0)
        legacy.ENsettimeparam(0, 3600)
        legacy.ENgetqualtype()
        legacy.ENsetqualtype(0, "", "", "")
        legacy.ENgetoption(0)
        legacy.ENsetoption(0, 1.0)
        legacy.ENgetversion()
        legacy.ENsolveH()
        legacy.ENopenH()
        legacy.ENinitH(0)
        legacy.ENrunH()
        legacy.ENnextH()
        legacy.ENcloseH()
        legacy.ENsolveQ()
        legacy.ENopenQ()
        legacy.ENinitQ(0)
        legacy.ENrunQ()
        legacy.ENnextQ()
        legacy.ENcloseQ()
        legacy.ENreport()
        legacy.ENresetreport()
        legacy.ENsetreport("ALL")
        legacy.ENgetstatistic(0)
        legacy.ENgetdemandmodel()
        legacy.ENsetdemandmodel(0,0,0,0)
        legacy.ENsaveinpfile("f")
        legacy.ENsavehydfile("f")
        legacy.ENusehydfile("f")
        legacy.ENsaveH()
        legacy.ENclose()
        legacy.ENsetjuncdata(1,0,0,"")
        legacy.ENsettankdata(1,0,0,0,0,0,0,"")
        legacy.ENgetcoord(1)
        legacy.ENsetcoord(1,0,0)
        legacy.ENsetpipedata(1,0,0,0,0)
        legacy.ENgetvertexcount(1)
        legacy.ENgetvertex(1,1)
        legacy.ENsetvertex(1,1,0,0)
        legacy.ENsetvertices(1,[1],[1])
        legacy.ENadddemand(1,0,"","")
        legacy.ENdeletedemand(1,1)
        legacy.ENgetnumdemands(1)
        legacy.ENgetbasedemand(1,1)
        legacy.ENsetbasedemand(1,1,1.0)
        legacy.ENaddpattern("P")
        legacy.ENgetpatternindex("P")
        legacy.ENgetpatternid(1)
        legacy.ENgetpatternlen(1)
        legacy.ENgetpatternvalue(1,1)
        legacy.ENdeletepattern(1)
        legacy.ENsetpattern(1,[1.0])
        legacy.ENsetpatternvalue(1,1,1.0)
        legacy.ENaddcurve("C")
        legacy.ENdeletecurve(1)
        legacy.ENgetcurveindex("C")
        legacy.ENgetcurveid(1)
        legacy.ENgetcurvelen(1)
        legacy.ENgetcurvetype(1)
        legacy.ENsetcurvetype(1,0)
        legacy.ENgetcurvevalue(1,1)
        legacy.ENsetcurvevalue(1,1,0,0)
        legacy.ENaddcontrol(1,1,1.0,1,1.0)
        legacy.ENdeletecontrol(1)
        legacy.ENgetcontrol(1)
        legacy.ENsetcontrol(1,1,1,1.0,1,1.0)
        legacy.ENsetstatusreport(1)
        legacy.ENgetnodevalues(0)
        legacy.ENgetlinkvalues(0)
        legacy.ENepanet("f", "r", "b")
        legacy.ENwriteline("l")

def test_missing_functions_final():
    """Trigger every single hasattr check fail in legacy.py."""
    class EmptyLib:
        def ENgeterror(self, code, buf, lens): return 0
    mock_lib = EmptyLib()
    with mock.patch("entoolkit.legacy._lib", mock_lib):
        checks = [
            lambda: legacy.ENgettitle(),
            lambda: legacy.ENgetcomment(1,1),
            lambda: legacy.ENgettag(1,1),
            lambda: legacy.ENsettag(1,1,"t"),
            lambda: legacy.ENdeletenode(1,0),
            lambda: legacy.ENadddemand(1,1.0),
            lambda: legacy.ENdeletedemand(1,1),
            lambda: legacy.ENgetnumdemands(1),
            lambda: legacy.ENgetbasedemand(1,1),
            lambda: legacy.ENsetbasedemand(1,1,1.0),
            lambda: legacy.ENsetjuncdata(1,0,0,""),
            lambda: legacy.ENsettankdata(1,0,0,0,0,0,0,""),
            lambda: legacy.ENgetcoord(1),
            lambda: legacy.ENsetcoord(1,0,0),
            lambda: legacy.ENsetpipedata(1,0,0,0,0),
            lambda: legacy.ENgetvertexcount(1),
            lambda: legacy.ENgetvertex(1,1),
            lambda: legacy.ENsetvertex(1,1,0,0),
            lambda: legacy.ENsetvertices(1,[1],[1]),
            lambda: legacy.ENaddcontrol(1,1,1,1,1),
            lambda: legacy.ENdeletecontrol(1),
            lambda: legacy.ENgetcontrol(1),
            lambda: legacy.ENsetcontrol(1,1,1,1,1,1),
            lambda: legacy.ENgetpatternid(1),
            lambda: legacy.ENgetpatternindex("p"),
            lambda: legacy.ENgetpatternlen(1),
            lambda: legacy.ENgetpatternvalue(1,1),
            lambda: legacy.ENaddpattern("p"),
            lambda: legacy.ENdeletepattern(1),
            lambda: legacy.ENsetpattern(1,[1]),
            lambda: legacy.ENsetpatternvalue(1,1,1),
            lambda: legacy.ENaddcurve("c"),
            lambda: legacy.ENdeletecurve(1),
            lambda: legacy.ENgetcurveindex("c"),
            lambda: legacy.ENgetcurveid(1),
            lambda: legacy.ENgetcurvelen(1),
            lambda: legacy.ENgetcurvetype(1),
            lambda: legacy.ENsetcurvetype(1,0),
            lambda: legacy.ENgetcurvevalue(1,1),
            lambda: legacy.ENsetcurvevalue(1,1,0,0),
            lambda: legacy.ENgetdemandmodel(),
            lambda: legacy.ENsetdemandmodel(0,0,0,0),
            lambda: legacy.ENdeletelink(1,0),
            lambda: legacy.ENsaveinpfile("f"),
            lambda: legacy.ENsavehydfile("f"),
            lambda: legacy.ENusehydfile("f"),
            lambda: legacy.ENsaveH()
        ]
        for c in checks:
            with pytest.raises(legacy.ENtoolkitError) as exc:
                c()
            assert "not supported" in str(exc.value)

def test_legacy_extra_loops():
    import unittest.mock as mock

    from entoolkit import legacy
    with mock.patch("entoolkit.legacy.ENgetcount", return_value=3):
        with mock.patch("entoolkit.legacy.ENgetnodevalue", return_value=0.0):
            with mock.patch("entoolkit.legacy.ENgetlinkvalue", return_value=0.0):
                legacy.ENgetnodevalues(0)
                legacy.ENgetlinkvalues(0)
