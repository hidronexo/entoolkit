"""
Legacy interface to the EPANET 2.2 toolkit (Global State API).

This module provides a direct mapping to the traditional EPANET functions. 
It operates on a single global project state and uses single precision 
(float) for most operations.

For thread-safe, multi-project, and high-precision (double) simulations, 
use `entoolkit.toolkit.EPANETProject` instead.
"""
import ctypes
import logging
import platform
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .constants import *

# --- general internal types ---
_Pchar = ctypes.c_char_p
_Pint = ctypes.POINTER(ctypes.c_int)
_Plong = ctypes.POINTER(ctypes.c_long)
_Pfloat = ctypes.POINTER(ctypes.c_float)
_Pdouble = ctypes.POINTER(ctypes.c_double)

# --- Library Loading ---

_OS_NAME = platform.system().lower()
_MACHINE = platform.machine().lower()
_BASE_PATH = Path(__file__).parent / "epanet"

# Architecture detection (x64, x86, arm64)
if "arm" in _MACHINE or "aarch64" in _MACHINE:
    _arch = "arm64" 
elif "64" in _MACHINE:
    _arch = "x64"
else:
    _arch = "x86"

# Library selection based on platform
_lib: ctypes.CDLL
if _OS_NAME == "windows":
    _lib_path = _BASE_PATH / f"windows-{_arch}" / "epanet2.dll"
    # Using WinDLL for __stdcall convention on Windows
    _lib = ctypes.WinDLL(str(_lib_path))
elif _OS_NAME == "darwin":
    _lib_path = _BASE_PATH / f"darwin-{_arch}" / "libepanet.dylib"
    _lib = ctypes.CDLL(str(_lib_path))
else: # Linux
    _lib_path = _BASE_PATH / f"linux-{_arch}" / "libepanet.so"
    _lib = ctypes.CDLL(str(_lib_path))

logger = logging.getLogger("entoolkit")
logger.info("Toolkit library loaded from %s", _lib_path)

# --- General Constants ---

MAX_LABEL_LEN = 31
MAX_TITLE_LEN = 80
ERR_MAX_CHAR = 259

# Module-level state flag to prevent double-close crashes.
# EPANET 2.2 legacy DLL corrupts the heap if ENclose() is called
# when no project is open.
_project_open = False


def ENinit(rpt_file: str = "", bin_file: str = "", units_type: int = EN_CFS, headloss_type: int = EN_HW) -> None:
    """Initializes the toolkit system with a new project.

    Args:
        rpt_file (str, optional): Path to the report file. Defaults to "".
        bin_file (str, optional): Path to the binary output file. Defaults to "".
        units_type (int, optional): Flow units code (e.g., EN_LPS, EN_CFS).
        headloss_type (int, optional): Headloss formula code (e.g., EN_HW, EN_DW).
    """
    global _project_open
    logger.info("Initializing toolkit: rpt='%s', bin='%s', units=%d, hl=%d", 
                rpt_file, bin_file, units_type, headloss_type)
    ierr = _lib.ENinit(ctypes.c_char_p(rpt_file.encode()),
                       ctypes.c_char_p(bin_file.encode()),
                       units_type, headloss_type)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    _project_open = True



def ENgettitle() -> Tuple[str, str, str]:
    """Retrieves the three title lines of the project."""
    line1 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
    line2 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
    line3 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
    if not hasattr(_lib, "ENgettitle"):
        raise ENtoolkitError(202, "ENgettitle not supported by this library version")
    ierr = _lib.ENgettitle(line1, line2, line3)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return line1.value.decode(), line2.value.decode(), line3.value.decode()


def ENsettitle(line1: str, line2: str, line3: str) -> None:
    """Sets the project title lines."""
    if not hasattr(_lib, "ENsettitle"):
        raise ENtoolkitError(202, "ENsettitle not supported by this library version")
    ierr = _lib.ENsettitle(ctypes.c_char_p(line1.encode()),
                           ctypes.c_char_p(line2.encode()),
                           ctypes.c_char_p(line3.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcomment(obj_type: int, index: int) -> str:
    """Retrieves a comment for a network object."""
    if not hasattr(_lib, "ENgetcomment"):
        raise ENtoolkitError(202, "ENgetcomment not supported by this library version")
    comment_buffer = ctypes.create_string_buffer(EN_MAXMSG + 1)
    ierr = _lib.ENgetcomment(obj_type, index, comment_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return comment_buffer.value.decode()


def ENsetcomment(obj_type: int, index: int, comment: str) -> None:
    """Sets the description comment for a network object."""
    if not hasattr(_lib, "ENsetcomment"):
        raise ENtoolkitError(202, "ENsetcomment not supported by this library version")
    ierr = _lib.ENsetcomment(obj_type, index, ctypes.c_char_p(comment.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgettag(obj_type: int, index: int) -> str:
    """Retrieves a tag for a network object."""
    if not hasattr(_lib, "ENgettag"):
        raise ENtoolkitError(202, "ENgettag not supported by this library version")
    tag_buffer = ctypes.create_string_buffer(EN_MAXMSG + 1)
    ierr = _lib.ENgettag(obj_type, index, tag_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return tag_buffer.value.decode()


def ENsettag(obj_type: int, index: int, tag: str) -> None:
    """Sets the tag string for a network object."""
    if not hasattr(_lib, "ENsettag"):
        raise ENtoolkitError(202, "ENsettag not supported by this library version")
    ierr = _lib.ENsettag(obj_type, index, ctypes.c_char_p(tag.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgeterror(error_code: int) -> str:
    """Retrieves the text of an error message."""
    if not hasattr(_lib, "ENgeterror"):
        return f"Toolkit Error {error_code} (library matching failed)"
    error_msg = ctypes.create_string_buffer(ERR_MAX_CHAR + 1)
    # We use ENgeterror directly from _lib to avoid chicken-egg in ENtoolkitError
    _lib.ENgeterror(error_code, error_msg, ERR_MAX_CHAR)
    return error_msg.value.decode()

# --- Safely set argtypes ---
_funcs_argtypes = {
    "ENinit": [_Pchar, _Pchar, ctypes.c_int, ctypes.c_int],
    "ENopen": [_Pchar, _Pchar, _Pchar],
    "ENclose": [],
    "ENgeterror": [ctypes.c_int, _Pchar, ctypes.c_int],
    "ENgetnodeindex": [_Pchar, _Pint],
    "ENgetnodeid": [ctypes.c_int, _Pchar],
    "ENgetnodetype": [ctypes.c_int, _Pint],
    "ENgetnodevalue": [ctypes.c_int, ctypes.c_int, _Pfloat],
    "ENaddnode": [_Pchar, ctypes.c_int, _Pint],
    "ENgetlinkindex": [_Pchar, _Pint],
    "ENgetlinkid": [ctypes.c_int, _Pchar],
    "ENgetlinktype": [ctypes.c_int, _Pint],
    "ENgetlinknodes": [ctypes.c_int, _Pint, _Pint],
    "ENgetlinkvalue": [ctypes.c_int, ctypes.c_int, _Pfloat],
    "ENaddlink": [_Pchar, ctypes.c_int, _Pchar, _Pchar, _Pint],
    "ENgetcount": [ctypes.c_int, _Pint],
    "ENgetflowunits": [_Pint],
    "ENgettimeparam": [ctypes.c_int, _Plong],
    "ENgetversion": [_Pint],
    "ENsetnodeid": [ctypes.c_int, _Pchar],
    "ENsetnodevalue": [ctypes.c_int, ctypes.c_int, ctypes.c_float],
    "ENsetlinkvalue": [ctypes.c_int, ctypes.c_int, ctypes.c_float],
    "ENsettimeparam": [ctypes.c_int, ctypes.c_long],
    "ENgetqualtype": [_Pint, _Pint],
    "ENsetqualtype": [ctypes.c_int, _Pchar, _Pchar, _Pchar],
    "ENgetoption": [ctypes.c_int, _Pfloat],
    "ENsetoption": [ctypes.c_int, ctypes.c_float],
    "ENsolveH": [],
    "ENopenH": [],
    "ENinitH": [ctypes.c_int],
    "ENrunH": [_Plong],
    "ENnextH": [_Plong],
    "ENcloseH": [],
    "ENsolveQ": [],
    "ENopenQ": [],
    "ENinitQ": [ctypes.c_int],
    "ENrunQ": [_Plong],
    "ENnextQ": [_Plong],
    "ENcloseQ": [],
    "ENreport": [],
    "ENresetreport": [],
    "ENsetreport": [_Pchar],
    "ENsetstatusreport": [ctypes.c_int],
    "ENgetstatistic": [ctypes.c_int, _Pfloat],
    "ENgetdemandmodel": [_Pint, _Pfloat, _Pfloat, _Pfloat],
    "ENsetdemandmodel": [ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float],
    "ENsaveinpfile": [_Pchar],
    "ENsavehydfile": [_Pchar],
    "ENusehydfile": [_Pchar],
    "ENsaveH": [],
    # Functions that might be missing in some 2.2 dists
    "ENgetcomment": [ctypes.c_int, ctypes.c_int, _Pchar],
    "ENsetcomment": [ctypes.c_int, ctypes.c_int, _Pchar],
    "ENgettag": [ctypes.c_int, ctypes.c_int, _Pchar],
    "ENsettag": [ctypes.c_int, ctypes.c_int, _Pchar],
    "ENsetjuncdata": [ctypes.c_int, ctypes.c_float, ctypes.c_float, _Pchar],
    "ENsettankdata": [ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, _Pchar],
    "ENgetcoord": [ctypes.c_int, _Pdouble, _Pdouble],
    "ENsetcoord": [ctypes.c_int, ctypes.c_double, ctypes.c_double],
    "ENsetpipedata": [ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float],
    "ENgetvertexcount": [ctypes.c_int, _Pint],
    "ENgetvertex": [ctypes.c_int, ctypes.c_int, _Pdouble, _Pdouble],
    "ENsetvertex": [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double],
    "ENadddemand": [ctypes.c_int, ctypes.c_float, _Pchar, _Pchar],
    "ENdeletedemand": [ctypes.c_int, ctypes.c_int],
    "ENgetnumdemands": [ctypes.c_int, _Pint],
    "ENgetbasedemand": [ctypes.c_int, ctypes.c_int, _Pfloat],
    "ENsetbasedemand": [ctypes.c_int, ctypes.c_int, ctypes.c_float],
    "ENsetvertices": [ctypes.c_int, _Pdouble, _Pdouble, ctypes.c_int],
    "ENgetpatternid": [ctypes.c_int, _Pchar],
    "ENgetpatternindex": [_Pchar, _Pint],
    "ENgetpatternlen": [ctypes.c_int, _Pint],
    "ENgetpatternvalue": [ctypes.c_int, ctypes.c_int, _Pfloat],
    "ENaddpattern": [_Pchar],
    "ENdeletepattern": [ctypes.c_int],
    "ENsetpattern": [ctypes.c_int, _Pfloat, ctypes.c_int],
    "ENsetpatternvalue": [ctypes.c_int, ctypes.c_int, ctypes.c_float],
    "ENaddcurve": [_Pchar],
    "ENdeletecurve": [ctypes.c_int],
    "ENgetcurveindex": [_Pchar, _Pint],
    "ENgetcurveid": [ctypes.c_int, _Pchar],
    "ENgetcurvelen": [ctypes.c_int, _Pint],
    "ENgetcurvetype": [ctypes.c_int, _Pint],
    "ENsetcurvetype": [ctypes.c_int, ctypes.c_int],
    "ENgetcurvevalue": [ctypes.c_int, ctypes.c_int, _Pfloat, _Pfloat],
    "ENsetcurvevalue": [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float],
    "ENwriteline": [_Pchar],
    "ENaddcontrol": [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_int, ctypes.c_float, _Pint],
    "ENdeletecontrol": [ctypes.c_int],
    "ENgetcontrol": [ctypes.c_int, _Pint, _Pint, _Pfloat, _Pint, _Pfloat],
    "ENsetcontrol": [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_int, ctypes.c_float],
    "ENdeletenode": [ctypes.c_int, ctypes.c_int],
    "ENdeletelink": [ctypes.c_int, ctypes.c_int],
    "ENgettitle": [_Pchar, _Pchar, _Pchar],
    "ENsettitle": [_Pchar, _Pchar, _Pchar],
}

for name, args in _funcs_argtypes.items():
    try:
        f = getattr(_lib, name)
        f.argtypes = args
        f.restype = ctypes.c_int
    except AttributeError:
        # Some functions might be missing in legacy context
        pass


class ENtoolkitError(Exception):
    """Exception raised for errors in the EPANET Toolkit."""
    def __init__(self, ierr: int, message: Optional[str] = None):
        self.ierr = ierr
        # Handle MagicMock or non-int ierr safely
        try:
            val = int(ierr)
            self.warning = val < 100
        except (TypeError, ValueError):
            self.warning = False
            
        if message:
            self.message = message
        else:
            try:
                self.message = ENgeterror(int(self.ierr))
            except Exception:
                self.message = f"Toolkit Error {self.ierr}"
        super().__init__(self.message)
        
        if self.warning:
            logger.warning("Toolkit Warning %s: %s", self.ierr, self.message)
        else:
            logger.error("Toolkit Error %s: %s", self.ierr, self.message)

    def __str__(self) -> str:
        return self.message


def ENepanet(inp_file: str, rpt_file: str = '', bin_file: str = '',
             vfunc: Optional[Callable[[str], None]] = None) -> None:
    """Runs a complete EPANET simulation at once.

    Args:
        inp_file (str): Path to the input file (.inp).
        rpt_file (str, optional): Path to the report file (.rpt).
        bin_file (str, optional): Path to the optional binary output file (.out).
        vfunc (callable, optional): Callback function that accepts a status string.
    """
    callback = None
    if vfunc is not None:
        cfunc = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
        callback = cfunc(lambda msg: vfunc(msg.decode()))

    logger.info("Running EPANET simulation: inp='%s', rpt='%s', bin='%s'", 
                inp_file, rpt_file, bin_file)
    ierr = _lib.ENepanet(ctypes.c_char_p(inp_file.encode()),
                         ctypes.c_char_p(rpt_file.encode()),
                         ctypes.c_char_p(bin_file.encode()),
                         callback)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENopen(inp_file: str, rpt_file: str = '', bin_file: str = '') -> None:
    """Opens an EPANET input file and associates it with the legacy project.

    Args:
        inp_file (str): Path to the .inp file.
        rpt_file (str, optional): Path to the report file to be created.
        bin_file (str, optional): Path to the binary output file to be created.
    """
    global _project_open
    logger.info("Opening project: inp='%s', rpt='%s', bin='%s'", inp_file, rpt_file, bin_file)
    ierr = _lib.ENopen(ctypes.c_char_p(inp_file.encode()),
                       ctypes.c_char_p(rpt_file.encode()),
                       ctypes.c_char_p(bin_file.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    _project_open = True


def ENclose() -> None:
    """Closes the EPANET toolkit and releases files.
    
    Safe to call multiple times — subsequent calls after the first are no-ops.
    This guards against heap corruption in the EPANET 2.2 legacy DLL.
    """
    global _project_open
    if not _project_open:
        logger.debug("ENclose called but no project is open, skipping")
        return
    logger.info("Closing toolkit")
    ierr = _lib.ENclose()
    _project_open = False
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetnodeindex(node_id: str) -> int:
    """Retrieves the internal index of a node by its ID.

    Args:
        node_id (str): The node ID string.

    Returns:
        int: The node index (1-based).
    """
    index_ptr = ctypes.c_int()
    ierr = _lib.ENgetnodeindex(ctypes.c_char_p(node_id.encode()), ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENgetnodeid(index: int) -> str:
    """Retrieves the ID string of a node given its index.

    Args:
        index (int): The node index (1-based).

    Returns:
        str: The node ID.
    """
    if not hasattr(_lib, "ENgetnodeid"):
        raise ENtoolkitError(202, "ENgetnodeid not supported by this library version")
    id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
    ierr = _lib.ENgetnodeid(index, id_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return id_buffer.value.decode()


def ENgetnodetype(index: int) -> int:
    """Retrieves the type of node (junction, reservoir, or tank).

    Args:
        index (int): The node index (1-based).

    Returns:
        int: The node type code (e.g., EN_JUNCTION, EN_TANK).
    """
    if not hasattr(_lib, "ENgetnodetype"):
        raise ENtoolkitError(202, "ENgetnodetype not supported by this library version")
    type_ptr = ctypes.c_int()
    ierr = _lib.ENgetnodetype(index, ctypes.byref(type_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return type_ptr.value


def ENgetnodevalue(index: int, param_code: int) -> float:
    """Retrieves a single-precision numeric property for a node.

    Args:
        index (int): The node index (1-based).
        param_code (int): Property code (e.g., EN_DEMAND, EN_PRESSURE).

    Returns:
        float: The property value.
    """
    value_ptr = ctypes.c_float()
    ierr = _lib.ENgetnodevalue(index, param_code, ctypes.byref(value_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(value_ptr.value)


def ENaddnode(node_id: str, node_type: int) -> int:
    """Adds a new node to the network."""
    index_ptr = ctypes.c_int()
    ierr = _lib.ENaddnode(ctypes.c_char_p(node_id.encode()), node_type, ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENdeletenode(index: int, action_code: int) -> None:
    """Deletes a node from the network."""
    if not hasattr(_lib, "ENdeletenode"):
        raise ENtoolkitError(202, "ENdeletenode not supported by this library version")
    ierr = _lib.ENdeletenode(index, action_code)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetnodeid(index: int, new_id: str) -> None:
    """Changes the ID for a node."""
    ierr = _lib.ENsetnodeid(index, ctypes.c_char_p(new_id.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENadddemand(node_index: int, base_demand: float, pattern_name: str = '', demand_name: str = '') -> None:
    """Appends a new demand to a junction node demands list."""
    if not hasattr(_lib, "ENadddemand"):
        raise ENtoolkitError(202, "ENadddemand not supported by this library version")
    ierr = _lib.ENadddemand(node_index, ctypes.c_float(base_demand),
                            ctypes.c_char_p(pattern_name.encode()),
                            ctypes.c_char_p(demand_name.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENdeletedemand(node_index: int, demand_index: int) -> None:
    """Deletes a demand from a junction node."""
    if not hasattr(_lib, "ENdeletedemand"):
        raise ENtoolkitError(202, "ENdeletedemand not supported by this library version")
    ierr = _lib.ENdeletedemand(node_index, demand_index)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetnumdemands(node_index: int) -> int:
    """Retrieves the number of demand categories for a junction node."""
    if not hasattr(_lib, "ENgetnumdemands"):
        raise ENtoolkitError(202, "ENgetnumdemands not supported by this library version")
    num_demands = ctypes.c_int()
    ierr = _lib.ENgetnumdemands(node_index, ctypes.byref(num_demands))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return num_demands.value


def ENgetbasedemand(node_index: int, demand_index: int) -> float:
    """Gets the base demand for one of a node's demand categories."""
    if not hasattr(_lib, "ENgetbasedemand"):
        raise ENtoolkitError(202, "ENgetbasedemand not supported by this library version")
    base_demand = ctypes.c_float()
    ierr = _lib.ENgetbasedemand(node_index, demand_index, ctypes.byref(base_demand))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(base_demand.value)


def ENsetbasedemand(node_index: int, demand_index: int, base_demand: float) -> None:
    """Sets the base demand for one of a node's demand categories."""
    if not hasattr(_lib, "ENsetbasedemand"):
        raise ENtoolkitError(202, "ENsetbasedemand not supported by this library version")
    ierr = _lib.ENsetbasedemand(node_index, demand_index, ctypes.c_float(base_demand))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetjuncdata(index: int, elev: float, dmnd: float, dmndpat: str) -> None:
    """Sets junction data."""
    if not hasattr(_lib, "ENsetjuncdata"):
        raise ENtoolkitError(202, "ENsetjuncdata not supported by this library version")
    ierr = _lib.ENsetjuncdata(index, ctypes.c_float(elev),
                             ctypes.c_float(dmnd),
                             ctypes.c_char_p(dmndpat.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsettankdata(index: int, elevation: float, init_level: float, min_level: float,
                  max_level: float, diameter: float, min_vol: float, vol_curve: str) -> None:
    """Sets tank parameters."""
    if not hasattr(_lib, "ENsettankdata"):
        raise ENtoolkitError(202, "ENsettankdata not supported by this library version")
    ierr = _lib.ENsettankdata(index, ctypes.c_float(elevation),
                              ctypes.c_float(init_level), ctypes.c_float(min_level),
                              ctypes.c_float(max_level), ctypes.c_float(diameter),
                              ctypes.c_float(min_vol), ctypes.c_char_p(vol_curve.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcoord(index: int) -> Tuple[float, float]:
    """Gets the X, Y coordinates for a node."""
    if not hasattr(_lib, "ENgetcoord"):
        raise ENtoolkitError(202, "ENgetcoord not supported by this library version")
    x = ctypes.c_double()
    y = ctypes.c_double()
    ierr = _lib.ENgetcoord(index, ctypes.byref(x), ctypes.byref(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return x.value, y.value


def ENsetcoord(index: int, x: float, y: float) -> None:
    """Sets the coordinates of a specific node."""
    if not hasattr(_lib, "ENsetcoord"):
        raise ENtoolkitError(202, "ENsetcoord not supported by this library version")
    ierr = _lib.ENsetcoord(index, ctypes.c_double(x), ctypes.c_double(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetnodevalue(index: int, param_code: int, value: float) -> None:
    """Sets a single-precision numeric property for a node.

    Args:
        index (int): The node index (1-based).
        param_code (int): Property code (e.g., EN_ELEVATION, EN_BASEDEMAND).
        value (float): The new property value.
    """
    ierr = _lib.ENsetnodevalue(index, param_code, ctypes.c_float(value))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetlinkindex(link_id: str) -> int:
    """Retrieves the internal index of a link by its ID.

    Args:
        link_id (str): The link ID string.

    Returns:
        int: The link index (1-based).
    """
    index_ptr = ctypes.c_int()
    ierr = _lib.ENgetlinkindex(ctypes.c_char_p(link_id.encode()), ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENgetlinkid(index: int) -> str:
    """Retrieves the ID string of a link given its index.

    Args:
        index (int): The link index (1-based).

    Returns:
        str: The link ID.
    """
    if not hasattr(_lib, "ENgetlinkid"):
        raise ENtoolkitError(202, "ENgetlinkid not supported by this library version")
    id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
    ierr = _lib.ENgetlinkid(index, id_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return id_buffer.value.decode()


def ENgetlinktype(index: int) -> int:
    """Gets the type code for a link."""
    if not hasattr(_lib, "ENgetlinktype"):
        raise ENtoolkitError(202, "ENgetlinktype not supported by this library version")
    type_ptr = ctypes.c_int()
    ierr = _lib.ENgetlinktype(index, ctypes.byref(type_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return type_ptr.value


def ENgetlinknodes(index: int) -> Tuple[int, int]:
    """Gets the indexes of the start and end nodes of a link."""
    if not hasattr(_lib, "ENgetlinknodes"):
        raise ENtoolkitError(202, "ENgetlinknodes not supported by this library version")
    from_node_ptr = ctypes.c_int()
    to_node_ptr = ctypes.c_int()
    ierr = _lib.ENgetlinknodes(index, ctypes.byref(from_node_ptr), ctypes.byref(to_node_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return from_node_ptr.value, to_node_ptr.value


def ENgetlinkvalue(index: int, param_code: int) -> float:
    """Retrieves a single-precision numeric property for a link.

    Args:
        index (int): The link index (1-based).
        param_code (int): Property code (e.g., EN_FLOW, EN_LENGTH).

    Returns:
        float: The property value.
    """
    value_ptr = ctypes.c_float()
    ierr = _lib.ENgetlinkvalue(index, param_code, ctypes.byref(value_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(value_ptr.value)


def ENaddlink(link_id: str, link_type: int, from_node: str, to_node: str) -> int:
    """Adds a new link to the network."""
    index_ptr = ctypes.c_int()
    ierr = _lib.ENaddlink(ctypes.c_char_p(link_id.encode()), link_type,
                          ctypes.c_char_p(from_node.encode()),
                          ctypes.c_char_p(to_node.encode()),
                          ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENdeletelink(index: int, action_code: int) -> None:
    """Deletes a link from the network."""
    if not hasattr(_lib, "ENdeletelink"):
        raise ENtoolkitError(202, "ENdeletelink not supported by this library version")
    ierr = _lib.ENdeletelink(index, action_code)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetpipedata(index: int, length: float, diameter: float, roughness: float, mloss: float) -> None:
    """Sets pipe parameters."""
    if not hasattr(_lib, "ENsetpipedata"):
        raise ENtoolkitError(202, "ENsetpipedata not supported by this library version")
    ierr = _lib.ENsetpipedata(index, ctypes.c_float(length), ctypes.c_float(diameter),
                              ctypes.c_float(roughness), ctypes.c_float(mloss))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetvertexcount(index: int) -> int:
    """Gets the number of vertices for a link."""
    if not hasattr(_lib, "ENgetvertexcount"):
        raise ENtoolkitError(202, "ENgetvertexcount not supported by this library version")
    count_ptr = ctypes.c_int()
    ierr = _lib.ENgetvertexcount(index, ctypes.byref(count_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return count_ptr.value


def ENgetvertex(index: int, vertex: int) -> Tuple[float, float]:
    """Gets the X, Y coordinates for a link vertex."""
    if not hasattr(_lib, "ENgetvertex"):
        raise ENtoolkitError(202, "ENgetvertex not supported by this library version")
    x = ctypes.c_double()
    y = ctypes.c_double()
    ierr = _lib.ENgetvertex(index, vertex, ctypes.byref(x), ctypes.byref(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return x.value, y.value


def ENsetvertex(index: int, vertex: int, x: float, y: float) -> None:
    """Sets the X, Y coordinates for a link vertex."""
    if not hasattr(_lib, "ENsetvertex"):
        raise ENtoolkitError(202, "ENsetvertex not supported by this library version")
    ierr = _lib.ENsetvertex(index, vertex, ctypes.c_double(x), ctypes.c_double(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetvertices(index: int, x: List[float], y: List[float]) -> None:
    """Sets the vertices for a specific link."""
    if not hasattr(_lib, "ENsetvertices"):
        raise ENtoolkitError(202, "ENsetvertices not supported by this library version")
    count = len(x)
    xc = (ctypes.c_double * count)(*x)
    yc = (ctypes.c_double * count)(*y)
    ierr = _lib.ENsetvertices(index, xc, yc, count)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetlinkvalue(index: int, param_code: int, value: float) -> None:
    """Sets the value of a specific link parameter."""
    ierr = _lib.ENsetlinkvalue(index, param_code, ctypes.c_float(value))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetpatternid(index: int) -> str:
    """Gets the ID for a time pattern from its index."""
    if not hasattr(_lib, "ENgetpatternid"):
        raise ENtoolkitError(202, "ENgetpatternid not supported by this library version")
    id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
    ierr = _lib.ENgetpatternid(index, id_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return id_buffer.value.decode()


def ENgetpatternindex(pattern_id: str) -> int:
    """Gets the index of a time pattern from its ID."""
    if not hasattr(_lib, "ENgetpatternindex"):
        raise ENtoolkitError(202, "ENgetpatternindex not supported by this library version")
    index_ptr = ctypes.c_int()
    ierr = _lib.ENgetpatternindex(ctypes.c_char_p(pattern_id.encode()), ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENgetpatternlen(index: int) -> int:
    """Gets the number of periods in a time pattern."""
    if not hasattr(_lib, "ENgetpatternlen"):
        raise ENtoolkitError(202, "ENgetpatternlen not supported by this library version")
    len_ptr = ctypes.c_int()
    ierr = _lib.ENgetpatternlen(index, ctypes.byref(len_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return len_ptr.value


def ENgetpatternvalue(index: int, period: int) -> float:
    """Gets the multiplier for a specific pattern period."""
    if not hasattr(_lib, "ENgetpatternvalue"):
        raise ENtoolkitError(202, "ENgetpatternvalue not supported by this library version")
    value_ptr = ctypes.c_float()
    ierr = _lib.ENgetpatternvalue(index, period, ctypes.byref(value_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(value_ptr.value)


def ENaddpattern(pattern_id: str) -> int:
    """Adds a new time pattern to the network.
    
    Note: The legacy C API does not return the index directly.
    After adding, we retrieve it with ENgetpatternindex.
    """
    if not hasattr(_lib, "ENaddpattern"):
        raise ENtoolkitError(202, "ENaddpattern not supported by this library version")
    ierr = _lib.ENaddpattern(ctypes.c_char_p(pattern_id.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return ENgetpatternindex(pattern_id)


def ENdeletepattern(index: int) -> None:
    """Deletes a time pattern from the network."""
    if not hasattr(_lib, "ENdeletepattern"):
        raise ENtoolkitError(202, "ENdeletepattern not supported by this library version")
    ierr = _lib.ENdeletepattern(index)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetpattern(index: int, factors: List[float]) -> None:
    """Sets all multipliers for a specific pattern."""
    if not hasattr(_lib, "ENsetpattern"):
        raise ENtoolkitError(202, "ENsetpattern not supported by this library version")
    num_factors = len(factors)
    cfactors = (ctypes.c_float * num_factors)(*factors)
    ierr = _lib.ENsetpattern(index, cfactors, num_factors)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetpatternvalue(index: int, period: int, value: float) -> None:
    """Sets the multiplier for a specific pattern period."""
    if not hasattr(_lib, "ENsetpatternvalue"):
        raise ENtoolkitError(202, "ENsetpatternvalue not supported by this library version")
    ierr = _lib.ENsetpatternvalue(index, period, ctypes.c_float(value))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENaddcurve(curve_id: str) -> int:
    """Adds a new data curve to the network.
    
    Note: The legacy C API does not return the index directly.
    After adding, we retrieve it with ENgetcurveindex.
    """
    if not hasattr(_lib, "ENaddcurve"):
        raise ENtoolkitError(202, "ENaddcurve not supported by this library version")
    ierr = _lib.ENaddcurve(ctypes.c_char_p(curve_id.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return ENgetcurveindex(curve_id)


def ENdeletecurve(index: int) -> None:
    """Deletes a data curve from the network."""
    if not hasattr(_lib, "ENdeletecurve"):
        raise ENtoolkitError(202, "ENdeletecurve not supported by this library version")
    ierr = _lib.ENdeletecurve(index)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcurveindex(curve_id: str) -> int:
    """Gets the index of a data curve from its ID."""
    if not hasattr(_lib, "ENgetcurveindex"):
        raise ENtoolkitError(202, "ENgetcurveindex not supported by this library version")
    index_ptr = ctypes.c_int()
    ierr = _lib.ENgetcurveindex(ctypes.c_char_p(curve_id.encode()), ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENgetcurveid(index: int) -> str:
    """Gets the ID for a data curve from its index."""
    if not hasattr(_lib, "ENgetcurveid"):
        raise ENtoolkitError(202, "ENgetcurveid not supported by this library version")
    id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
    ierr = _lib.ENgetcurveid(index, id_buffer)
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return id_buffer.value.decode()


def ENgetcurvelen(index: int) -> int:
    """Gets the number of points in a data curve."""
    if not hasattr(_lib, "ENgetcurvelen"):
        raise ENtoolkitError(202, "ENgetcurvelen not supported by this library version")
    len_ptr = ctypes.c_int()
    ierr = _lib.ENgetcurvelen(index, ctypes.byref(len_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return len_ptr.value


def ENgetcurvetype(index: int) -> int:
    """Gets the type of a data curve."""
    if not hasattr(_lib, "ENgetcurvetype"):
        raise ENtoolkitError(202, "ENgetcurvetype not supported by this library version")
    type_ptr = ctypes.c_int()
    ierr = _lib.ENgetcurvetype(index, ctypes.byref(type_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return type_ptr.value


def ENsetcurvetype(index: int, type_code: int) -> None:
    """Sets the type of a data curve."""
    if not hasattr(_lib, "ENsetcurvetype"):
        raise ENtoolkitError(202, "ENsetcurvetype not supported by this library version")
    ierr = _lib.ENsetcurvetype(index, type_code)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcurvevalue(index: int, point_index: int) -> Tuple[float, float]:
    """Gets the X and Y values for a point in a data curve."""
    if not hasattr(_lib, "ENgetcurvevalue"):
        raise ENtoolkitError(202, "ENgetcurvevalue not supported by this library version")
    x = ctypes.c_float()
    y = ctypes.c_float()
    ierr = _lib.ENgetcurvevalue(index, point_index, ctypes.byref(x), ctypes.byref(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(x.value), float(y.value)


def ENsetcurvevalue(index: int, point_index: int, x: float, y: float) -> None:
    """Sets the X and Y values for a point in a data curve."""
    if not hasattr(_lib, "ENsetcurvevalue"):
        raise ENtoolkitError(202, "ENsetcurvevalue not supported by this library version")
    ierr = _lib.ENsetcurvevalue(index, point_index, ctypes.c_float(x), ctypes.c_float(y))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcount(count_code: int) -> int:
    """Retrieves the number of objects of a specific type.

    Args:
        count_code (int): Object type code (e.g., EN_NODECOUNT, EN_LINKCOUNT).

    Returns:
        int: The number of objects.
    """
    count_ptr = ctypes.c_int()
    ierr = _lib.ENgetcount(count_code, ctypes.byref(count_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return count_ptr.value


def ENgetflowunits() -> int:
    """Gets the flow units code for the project."""
    if not hasattr(_lib, "ENgetflowunits"):
        raise ENtoolkitError(202, "ENgetflowunits not supported by this library version")
    units_ptr = ctypes.c_int()
    ierr = _lib.ENgetflowunits(ctypes.byref(units_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return units_ptr.value


def ENgettimeparam(param_code: int) -> int:
    """Gets the value of a specific time parameter."""
    time_ptr = ctypes.c_long()
    ierr = _lib.ENgettimeparam(param_code, ctypes.byref(time_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return time_ptr.value


def ENsettimeparam(param_code: int, time_value: int) -> None:
    """Sets the value of a specific time parameter."""
    ierr = _lib.ENsettimeparam(param_code, ctypes.c_long(time_value))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetqualtype() -> Tuple[int, int]:
    """Gets the type of water quality analysis and trace node."""
    q_ptr = ctypes.c_int()
    t_ptr = ctypes.c_int()
    ierr = _lib.ENgetqualtype(ctypes.byref(q_ptr), ctypes.byref(t_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return q_ptr.value, t_ptr.value


def ENsetqualtype(qual_code: int, chem_name: str, chem_units: str, trace_node: str) -> None:
    """Sets the water quality analysis parameters."""
    ierr = _lib.ENsetqualtype(qual_code,
                              ctypes.c_char_p(chem_name.encode()),
                              ctypes.c_char_p(chem_units.encode()),
                              ctypes.c_char_p(trace_node.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetoption(option_code: int) -> float:
    """Gets the value of a simulation option."""
    value_ptr = ctypes.c_float()
    ierr = _lib.ENgetoption(option_code, ctypes.byref(value_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(value_ptr.value)

def ENsetoption(option_code: int, value: float) -> None:
    """Sets the value of a simulation option."""
    ierr = _lib.ENsetoption(option_code, ctypes.c_float(value))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetversion() -> int:
    """Gets the version number of the EPANET toolkit."""
    if not hasattr(_lib, "ENgetversion"):
        raise ENtoolkitError(202, "ENgetversion not supported by this library version")
    version_ptr = ctypes.c_int()
    ierr = _lib.ENgetversion(ctypes.byref(version_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return version_ptr.value


def ENsolveH() -> None:
    """Solves the hydraulics for the current project."""
    ierr = _lib.ENsolveH()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENopenH() -> None:
    """Opens the hydraulic solver."""
    ierr = _lib.ENopenH()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENinitH(init_flag: int = 0) -> None:
    """Initializes the hydraulic solver."""
    ierr = _lib.ENinitH(init_flag)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENrunH() -> int:
    """Executes a single step of the hydraulic simulation. Returns simulation time."""
    time_ptr = ctypes.c_long()
    ierr = _lib.ENrunH(ctypes.byref(time_ptr))
    if ierr >= 100:
        raise ENtoolkitError(ierr)
    return time_ptr.value


def ENnextH() -> int:
    """Advances one time step in the simulation. Returns time remaining."""
    deltat_ptr = ctypes.c_long()
    ierr = _lib.ENnextH(ctypes.byref(deltat_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return deltat_ptr.value


def ENcloseH() -> None:
    """Closes the hydraulic solver."""
    ierr = _lib.ENcloseH()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsolveQ() -> None:
    """Solves water quality for current project."""
    ierr = _lib.ENsolveQ()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENopenQ() -> None:
    """Opens the quality solver."""
    ierr = _lib.ENopenQ()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENinitQ(init_flag: int = 0) -> None:
    """Initializes the quality solver."""
    ierr = _lib.ENinitQ(init_flag)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENrunQ() -> int:
    """Runs one quality simulation step. Returns time."""
    time_ptr = ctypes.c_long()
    ierr = _lib.ENrunQ(ctypes.byref(time_ptr))
    if ierr >= 100:
        raise ENtoolkitError(ierr)
    return time_ptr.value


def ENnextQ() -> int:
    """Advances one quality simulation step. Returns time remaining."""
    deltat_ptr = ctypes.c_long()
    ierr = _lib.ENnextQ(ctypes.byref(deltat_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return deltat_ptr.value


def ENcloseQ() -> None:
    """Closes quality solver."""
    ierr = _lib.ENcloseQ()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsaveH() -> None:
    """Saves hydraulic results."""
    if not hasattr(_lib, "ENsaveH"):
        raise ENtoolkitError(202, "ENsaveH not supported by this library version")
    ierr = _lib.ENsaveH()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsaveinpfile(file_name: str) -> None:
    """Saves current network state as an .inp file."""
    if not hasattr(_lib, "ENsaveinpfile"):
        raise ENtoolkitError(202, "ENsaveinpfile not supported by this library version")
    ierr = _lib.ENsaveinpfile(ctypes.c_char_p(file_name.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsavehydfile(file_name: str) -> None:
    """Saves binary hydraulics results."""
    if not hasattr(_lib, "ENsavehydfile"):
        raise ENtoolkitError(202, "ENsavehydfile not supported by this library version")
    ierr = _lib.ENsavehydfile(ctypes.c_char_p(file_name.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENusehydfile(file_name: str) -> None:
    """Uses a pre-calculated hydraulics binary file."""
    if not hasattr(_lib, "ENusehydfile"):
        raise ENtoolkitError(202, "ENusehydfile not supported by this library version")
    ierr = _lib.ENusehydfile(ctypes.c_char_p(file_name.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENreport() -> None:
    """Generates the report file."""
    ierr = _lib.ENreport()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENresetreport() -> None:
    """Resets all report commands."""
    ierr = _lib.ENresetreport()
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetreport(command: str) -> None:
    """Applies a specific report configuration command."""
    ierr = _lib.ENsetreport(ctypes.c_char_p(command.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENwriteline(line: str) -> None:
    """Writes a line of text to the report file."""
    ierr = _lib.ENwriteline(ctypes.c_char_p(line.encode()))
    if ierr != 0:
        raise ENtoolkitError(ierr)

# --- Convenience functions for missing array exports ---

def ENgetnodevalues(property_code: int) -> List[float]:
    """Gets values for a property for all nodes via loop (legacy array export missing in 2.2)."""
    count = ENgetcount(EN_NODECOUNT)
    return [ENgetnodevalue(i, property_code) for i in range(1, count + 1)]


def ENgetlinkvalues(property_code: int) -> List[float]:
    """Gets values for a property for all links via loop (legacy array export missing in 2.2)."""
    count = ENgetcount(EN_LINKCOUNT)
    return [ENgetlinkvalue(i, property_code) for i in range(1, count + 1)]




def ENaddcontrol(type: int, link_index: int, setting: float, node_index: int, level: float) -> int:
    """Adds a new simple control to the network.

    Args:
        type (int): Control type (e.g., EN_LOWLEVEL, EN_TIMER).
        link_index (int): Index of the link to be controlled.
        setting (float): Control setting (0/1 for open/closed, or valve setting).
        node_index (int): Index of the controlling node.
        level (float): Level or pressure value that triggers the control.

    Returns:
        int: The index of the newly added control.
    """
    index_ptr = ctypes.c_int()
    if not hasattr(_lib, "ENaddcontrol"):
        raise ENtoolkitError(202, "ENaddcontrol not supported by this library version")
    ierr = _lib.ENaddcontrol(type, link_index, ctypes.c_float(setting),
                             node_index, ctypes.c_float(level), ctypes.byref(index_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return index_ptr.value


def ENdeletecontrol(index: int) -> None:
    """Deletes an existing simple control.

    Args:
        index (int): The index of the control to delete.
    """
    if not hasattr(_lib, "ENdeletecontrol"):
        raise ENtoolkitError(202, "ENdeletecontrol not supported by this library version")
    ierr = _lib.ENdeletecontrol(index)
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetcontrol(index: int) -> Tuple[int, int, float, int, float]:
    """Retrieves parameters for a specific simple control.

    Args:
        index (int): The index of the control.

    Returns:
        Tuple[int, int, float, int, float]: (type, link_index, setting, node_index, level).
    """
    if not hasattr(_lib, "ENgetcontrol"):
        raise ENtoolkitError(202, "ENgetcontrol not supported by this library version")
    type_ptr = ctypes.c_int()
    link_ptr = ctypes.c_int()
    setting_ptr = ctypes.c_float()
    node_ptr = ctypes.c_int()
    level_ptr = ctypes.c_float()
    ierr = _lib.ENgetcontrol(index, ctypes.byref(type_ptr), ctypes.byref(link_ptr),
                             ctypes.byref(setting_ptr), ctypes.byref(node_ptr),
                             ctypes.byref(level_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return type_ptr.value, link_ptr.value, float(setting_ptr.value), node_ptr.value, float(level_ptr.value)


def ENsetcontrol(index: int, type: int, link_index: int, setting: float, node_index: int, level: float) -> None:
    """Sets the parameters for an existing simple control.

    Args:
        index (int): The control index.
        type (int): Control type code.
        link_index (int): Link index.
        setting (float): Control setting.
        node_index (int): Node index.
        level (float): Control trigger level.
    """
    if not hasattr(_lib, "ENsetcontrol"):
        raise ENtoolkitError(202, "ENsetcontrol not supported by this library version")
    ierr = _lib.ENsetcontrol(index, type, link_index, ctypes.c_float(setting),
                             node_index, ctypes.c_float(level))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENgetstatistic(type_code: int) -> float:
    """Retrieves a simulation statistic (e.g., iterations, relative error).

    Args:
        type_code (int): Statistic type code (e.g., EN_ITERATIONS).

    Returns:
        float: The value of the statistic.
    """
    value_ptr = ctypes.c_float()
    ierr = _lib.ENgetstatistic(type_code, ctypes.byref(value_ptr))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return float(value_ptr.value)


def ENgetdemandmodel() -> Tuple[int, float, float, float]:
    """Retrieves the current demand model and its parameters (EPANET 2.2+).

    Returns:
        Tuple[int, float, float, float]: (model_type, pmin, preq, pexp).
    """
    if not hasattr(_lib, "ENgetdemandmodel"):
        raise ENtoolkitError(202, "ENgetdemandmodel not supported by this library version")
    model = ctypes.c_int()
    pmin = ctypes.c_float()
    preq = ctypes.c_float()
    pexp = ctypes.c_float()
    ierr = _lib.ENgetdemandmodel(ctypes.byref(model), ctypes.byref(pmin),
                                 ctypes.byref(preq), ctypes.byref(pexp))
    if ierr != 0:
        raise ENtoolkitError(ierr)
    return model.value, float(pmin.value), float(preq.value), float(pexp.value)


def ENsetdemandmodel(model: int, pmin: float, preq: float, pexp: float) -> None:
    """Sets the demand model and its parameters.

    Args:
        model (int): Demand model type (e.g., EN_DDA, EN_PDA).
        pmin (float): Minimum pressure.
        preq (float): Required pressure.
        pexp (float): Pressure exponent.
    """
    if not hasattr(_lib, "ENsetdemandmodel"):
        raise ENtoolkitError(202, "ENsetdemandmodel not supported by this library version")
    ierr = _lib.ENsetdemandmodel(model, ctypes.c_float(pmin),
                                 ctypes.c_float(preq), ctypes.c_float(pexp))
    if ierr != 0:
        raise ENtoolkitError(ierr)


def ENsetstatusreport(status_level: int) -> None:
    """Sets the level of status reporting.

    Args:
        status_level (int): 0 = none, 1 = normal, 2 = full.
    """
    ierr = _lib.ENsetstatusreport(status_level)
    if ierr:
        raise ENtoolkitError(ierr)



