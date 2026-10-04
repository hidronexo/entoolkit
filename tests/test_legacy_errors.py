import unittest.mock as mock

import pytest

from entoolkit import legacy


def test_legacy_error_paths():
    """Trigger the 'if ierr: raise ENtoolkitError(ierr)' branch in legacy functions."""
    
    # We'll mock the whole _lib object to return 200 for any call
    mock_lib = mock.MagicMock()
    # Configure all calls to return 200
    mock_lib.configure_mock(**{name: mock.Mock(return_value=200) for name in [
        "ENinit", "ENgettitle", "ENsettitle", "ENgetcomment", "ENsetcomment",
        "ENgettag", "ENsettag", "ENopen", "ENclose", "ENgetnodeindex",
        "ENgetnodeid", "ENgetnodetype", "ENgetnodevalue", "ENaddnode",
        "ENdeletenode", "ENsetnodeid", "ENadddemand", "ENdeletedemand",
        "ENgetnumdemands", "ENgetbasedemand", "ENsetbasedemand", "ENsetjuncdata",
        "ENsettankdata", "ENgetcoord", "ENsetcoord", "ENsetnodevalue",
        "ENgetlinkindex", "ENgetlinkid", "ENgetlinktype", "ENgetlinknodes",
        "ENgetlinkvalue", "ENaddlink", "ENdeletelink", "ENsetpipedata",
        "ENgetvertexcount", "ENgetvertex", "ENsetvertex", "ENsetvertices",
        "ENsetlinkvalue", "ENgetpatternid", "ENgetpatternindex", "ENgetpatternlen",
        "ENgetpatternvalue", "ENaddpattern", "ENdeletepattern", "ENsetpattern",
        "ENsetpatternvalue", "ENaddcurve", "ENdeletecurve", "ENgetcurveindex",
        "ENgetcurveid", "ENgetcurvelen", "ENgetcurvetype", "ENsetcurvetype",
        "ENgetcurvevalue", "ENsetcurvevalue", "ENgetcount", "ENgetflowunits",
        "ENgettimeparam", "ENsettimeparam", "ENgetqualtype", "ENsetqualtype",
        "ENgetoption", "ENsetoption", "ENgetversion", "ENsolveH", "ENopenH",
        "ENinitH", "ENcloseH", "ENsolveQ", "ENopenQ", "ENinitQ", "ENcloseQ",
        "ENsaveH", "ENsaveinpfile", "ENsavehydfile", "ENusehydfile", "ENreport",
        "ENresetreport", "ENsetreport", "ENaddcontrol", "ENdeletecontrol",
        "ENgetcontrol", "ENsetcontrol", "ENgetstatistic", "ENgetdemandmodel",
        "ENsetdemandmodel", "ENsetstatusreport"
    ]})

    # Also mock ENgeterror so it doesn't crash trying to use mock_lib inside ENgeterror
    with mock.patch("entoolkit.legacy._lib", mock_lib), \
         mock.patch("entoolkit.legacy.ENgeterror", return_value="Mock Error"), \
         mock.patch("entoolkit.legacy._project_open", True):
        
        functions_to_test = [
            ("ENinit", ["", "", 0, 0]),
            ("ENgettitle", []),
            ("ENsettitle", ["", "", ""]),
            ("ENgetcomment", [1, 1]),
            ("ENsetcomment", [1, 1, ""]),
            ("ENgettag", [1, 1]),
            ("ENsettag", [1, 1, ""]),
            ("ENopen", ["nonexistent.inp"]),
            ("ENclose", []),
            ("ENgetnodeindex", [""]),
            ("ENgetnodeid", [1]),
            ("ENgetnodetype", [1]),
            ("ENgetnodevalue", [1, 0]),
            ("ENaddnode", ["", 0]),
            ("ENdeletenode", [1, 0]),
            ("ENsetnodeid", [1, ""]),
            ("ENadddemand", [1, 0.0]),
            ("ENdeletedemand", [1, 1]),
            ("ENgetnumdemands", [1]),
            ("ENgetbasedemand", [1, 1]),
            ("ENsetbasedemand", [1, 1, 0.0]),
            ("ENsetjuncdata", [1, 0, 0, ""]),
            ("ENsettankdata", [1, 0, 0, 0, 0, 0, 0, ""]),
            ("ENgetcoord", [1]),
            ("ENsetcoord", [1, 0, 0]),
            ("ENsetnodevalue", [1, 0, 0]),
            ("ENgetlinkindex", [""]),
            ("ENgetlinkid", [1]),
            ("ENgetlinktype", [1]),
            ("ENgetlinknodes", [1]),
            ("ENgetlinkvalue", [1, 0]),
            ("ENaddlink", ["", 0, "", ""]),
            ("ENdeletelink", [1, 0]),
            ("ENsetpipedata", [1, 0, 0, 0, 0]),
            ("ENgetvertexcount", [1]),
            ("ENgetvertex", [1, 1]),
            ("ENsetvertex", [1, 1, 0, 0]),
            ("ENsetvertices", [1, [], []]),
            ("ENsetlinkvalue", [1, 0, 0]),
            ("ENgetpatternid", [1]),
            ("ENgetpatternindex", [""]),
            ("ENgetpatternlen", [1]),
            ("ENgetpatternvalue", [1, 1]),
            ("ENaddpattern", [""]),
            ("ENdeletepattern", [1]),
            ("ENsetpattern", [1, []]),
            ("ENsetpatternvalue", [1, 1, 0]),
            ("ENaddcurve", [""]),
            ("ENdeletecurve", [1]),
            ("ENgetcurveindex", [""]),
            ("ENgetcurveid", [1]),
            ("ENgetcurvelen", [1]),
            ("ENgetcurvetype", [1]),
            ("ENsetcurvetype", [1, 0]),
            ("ENgetcurvevalue", [1, 1]),
            ("ENsetcurvevalue", [1, 1, 0, 0]),
            ("ENgetcount", [0]),
            ("ENgetflowunits", []),
            ("ENgettimeparam", [0]),
            ("ENsettimeparam", [0, 0]),
            ("ENgetqualtype", []),
            ("ENsetqualtype", [0, "", "", ""]),
            ("ENgetoption", [0]),
            ("ENsetoption", [0, 0]),
            ("ENgetversion", []),
            ("ENsolveH", []),
            ("ENopenH", []),
            ("ENinitH", []),
            ("ENcloseH", []),
            ("ENsolveQ", []),
            ("ENopenQ", []),
            ("ENinitQ", []),
            ("ENcloseQ", []),
            ("ENsaveH", []),
            ("ENsaveinpfile", [""]),
            ("ENsavehydfile", [""]),
            ("ENusehydfile", [""]),
            ("ENreport", []),
            ("ENresetreport", []),
            ("ENsetreport", [""]),
            ("ENaddcontrol", [0, 1, 0.0, 1, 0.0]),
            ("ENdeletecontrol", [1]),
            ("ENgetcontrol", [1]),
            ("ENsetcontrol", [1, 0, 1, 0, 1, 0]),
            ("ENgetstatistic", [0]),
            ("ENgetdemandmodel", []),
            ("ENsetdemandmodel", [0, 0, 0, 0]),
            ("ENsetstatusreport", [0]),
        ]
        
        for func_name, args in functions_to_test:
            func = getattr(legacy, func_name)
            with pytest.raises(legacy.ENtoolkitError):
                func(*args)
