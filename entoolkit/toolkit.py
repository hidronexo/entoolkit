"""
High-level, thread-safe interface to the EPANET 2.2 toolkit.

This module provides the EPANETProject class, which uses project handles 
to manage multiple network simulations simultaneously with double precision.
"""
import ctypes
import logging
from typing import List, Tuple

from .constants import *
from .legacy import ERR_MAX_CHAR, MAX_LABEL_LEN, MAX_TITLE_LEN, ENtoolkitError, _lib

logger = logging.getLogger("entoolkit")

# Define core project creation/deletion types
_lib.EN_createproject.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
_lib.EN_createproject.restype = ctypes.c_int

_lib.EN_deleteproject.argtypes = [ctypes.c_void_p]
_lib.EN_deleteproject.restype = ctypes.c_int

_lib.EN_geterror.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
_lib.EN_geterror.restype = ctypes.c_int

_lib.EN_init.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
_lib.EN_init.restype = ctypes.c_int

_lib.EN_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_lib.EN_open.restype = ctypes.c_int

_lib.EN_close.argtypes = [ctypes.c_void_p]
_lib.EN_close.restype = ctypes.c_int

_lib.EN_solveH.argtypes = [ctypes.c_void_p]
_lib.EN_solveH.restype = ctypes.c_int

_lib.EN_getnodeindex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
_lib.EN_getnodeindex.restype = ctypes.c_int

_lib.EN_getnodeid.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
_lib.EN_getnodeid.restype = ctypes.c_int

_lib.EN_getnodevalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getnodevalue.restype = ctypes.c_int

_lib.EN_setnodevalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double]
_lib.EN_setnodevalue.restype = ctypes.c_int

_lib.EN_getlinkindex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
_lib.EN_getlinkindex.restype = ctypes.c_int

_lib.EN_getlinkid.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
_lib.EN_getlinkid.restype = ctypes.c_int

_lib.EN_getlinkvalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getlinkvalue.restype = ctypes.c_int

_lib.EN_setlinkvalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double]
_lib.EN_setlinkvalue.restype = ctypes.c_int

_lib.EN_getcount.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
_lib.EN_getcount.restype = ctypes.c_int

_lib.EN_addnode.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
_lib.EN_addnode.restype = ctypes.c_int

_lib.EN_addlink.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
_lib.EN_addlink.restype = ctypes.c_int

_lib.EN_getnumdemands.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
_lib.EN_getnumdemands.restype = ctypes.c_int

_lib.EN_getbasedemand.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getbasedemand.restype = ctypes.c_int

_lib.EN_setbasedemand.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double]
_lib.EN_setbasedemand.restype = ctypes.c_int

_lib.EN_adddemand.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_char_p, ctypes.c_char_p]
_lib.EN_adddemand.restype = ctypes.c_int

_lib.EN_deletedemand.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
_lib.EN_deletedemand.restype = ctypes.c_int

_lib.EN_setdemandmodel.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double]
_lib.EN_setdemandmodel.restype = ctypes.c_int

_lib.EN_setqualtype.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_lib.EN_setqualtype.restype = ctypes.c_int

_lib.EN_solveQ.argtypes = [ctypes.c_void_p]
_lib.EN_solveQ.restype = ctypes.c_int

_lib.EN_addpattern.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
_lib.EN_addpattern.restype = ctypes.c_int

_lib.EN_setpattern.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.EN_setpattern.restype = ctypes.c_int

_lib.EN_getpatternvalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getpatternvalue.restype = ctypes.c_int

# --- Advanced Project Management Functions ---

# Define EN_getstatistic
_lib.EN_getstatistic.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getstatistic.restype = ctypes.c_int

# Define EN_getoption
_lib.EN_getoption.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
_lib.EN_getoption.restype = ctypes.c_int

# Define EN_setoption
_lib.EN_setoption.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
_lib.EN_setoption.restype = ctypes.c_int

# Define EN_gettitle
_lib.EN_gettitle.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_lib.EN_gettitle.restype = ctypes.c_int

# Define EN_settitle
_lib.EN_settitle.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_lib.EN_settitle.restype = ctypes.c_int

# Define EN_addcontrol
_lib.EN_addcontrol.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_int)]
_lib.EN_addcontrol.restype = ctypes.c_int

# Define EN_getcontrol
_lib.EN_getcontrol.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double)]
_lib.EN_getcontrol.restype = ctypes.c_int

# Define EN_setcontrol
_lib.EN_setcontrol.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_int, ctypes.c_double]
_lib.EN_setcontrol.restype = ctypes.c_int

# Define EN_deletecontrol
_lib.EN_deletecontrol.argtypes = [ctypes.c_void_p, ctypes.c_int]
_lib.EN_deletecontrol.restype = ctypes.c_int

# Define EN_getpatternindex
_lib.EN_getpatternindex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
_lib.EN_getpatternindex.restype = ctypes.c_int

class EPANETProject:
    """A thread-safe interface to an EPANET project handle.
    
    This class wraps the EPANET 2.2 handle-based API, allowing multiple
    projects to be managed simultaneously in the same process.
    
    In contrast to the legacy API (entoolkit.legacy), this class uses 
    **double precision** (64-bit) for all property values, ensuring 
    higher numerical accuracy.
    """
    
    def __init__(self):
        """Initializes a new EPANET project handle."""
        self.ph = ctypes.c_void_p()
        logger.info("Creating new EPANET project handle")
        ierr = _lib.EN_createproject(ctypes.byref(self.ph))
        if ierr:
            raise ENtoolkitError(ierr)
            
    def __del__(self):
        # We don't call EN_deleteproject in __del__ because it can cause 
        # issues during interpreter shutdown if _lib is already cleaned up.
        # User should call delete() explicitly or use a context manager.
        pass

    def delete(self):
        """Deletes the project and frees all associated memory."""
        if hasattr(self, 'ph') and self.ph:
            logger.info("Deleting EPANET project handle")
            _lib.EN_deleteproject(self.ph)
            self.ph = None

    def _check(self, ierr: int):
        if ierr:
            msg = ctypes.create_string_buffer(ERR_MAX_CHAR)
            _lib.EN_geterror(ierr, msg, ERR_MAX_CHAR)
            err_msg = msg.value.decode()
            raise ENtoolkitError(ierr, err_msg)

    # --- Project Management ---

    def init(self, rpt_file: str = "", bin_file: str = "", units: int = EN_CFS, hl: int = EN_HW):
        """Initializes a new project with specific units and headloss formula.

        Args:
            rpt_file (str): Path to the report file (default is no file).
            bin_file (str): Path to the binary output file (default is no file).
            units (int): Flow units code (e.g., EN_LPS, EN_CFS).
            hl (int): Headloss formula code (e.g., EN_HW, EN_DW).
        """
        logger.info("Initializing project: rpt='%s', bin='%s', units=%d, hl=%d", 
                    rpt_file, bin_file, units, hl)
        self._check(_lib.EN_init(self.ph, 
                                 ctypes.c_char_p(rpt_file.encode()),
                                 ctypes.c_char_p(bin_file.encode()),
                                 units, hl))

    def open(self, inp_file: str, rpt_file: str = '', bin_file: str = ''):
        """Opens an EPANET project from an input file.

        Args:
            inp_file (str): Path to the .inp file.
            rpt_file (str): Path to the report file to be created.
            bin_file (str): Path to the binary output file to be created.
        """
        logger.info("Opening project: inp='%s', rpt='%s', bin='%s'", inp_file, rpt_file, bin_file)
        self._check(_lib.EN_open(self.ph, 
                                 ctypes.c_char_p(inp_file.encode()),
                                 ctypes.c_char_p(rpt_file.encode()),
                                 ctypes.c_char_p(bin_file.encode())))

    def close(self):
        """Closes the currently open project and releases file handles."""
        logger.info("Closing project")
        self._check(_lib.EN_close(self.ph))

    def solveH(self):
        """Runs a complete hydraulic simulation and saves results to files."""
        logger.info("Solving hydraulics")
        self._check(_lib.EN_solveH(self.ph))

    # --- Node Properties (Double Precision) ---

    def getnodeindex(self, node_id: str) -> int:
        """Retrieves the internal index of a node by its ID.

        Args:
            node_id (str): The node ID string.

        Returns:
            int: The node index (1-based).
        """
        index = ctypes.c_int()
        self._check(_lib.EN_getnodeindex(self.ph, ctypes.c_char_p(node_id.encode()), ctypes.byref(index)))
        return index.value

    def getnodeid(self, index: int) -> str:
        """Retrieves the ID string of a node by its index.

        Args:
            index (int): The node index (1-based).

        Returns:
            str: The node ID.
        """
        id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
        self._check(_lib.EN_getnodeid(self.ph, index, id_buffer))
        return id_buffer.value.decode()

    def getnodevalue(self, index: int, prop: int) -> float:
        """Retrieves a double-precision property value for a node.

        Args:
            index (int): The node index (1-based).
            prop (int): Property code (e.g., EN_DEMAND, EN_PRESSURE).

        Returns:
            float: The property value.
        """
        val = ctypes.c_double()
        self._check(_lib.EN_getnodevalue(self.ph, index, prop, ctypes.byref(val)))
        return float(val.value)

    def setnodevalue(self, index: int, prop: int, value: float):
        """Sets a property value for a node (Double Precision).

        Args:
            index (int): The node index (1-based).
            prop (int): Property code (e.g., EN_ELEVATION, EN_BASEDEMAND).
            value (float): The value to set.
        """
        self._check(_lib.EN_setnodevalue(self.ph, index, prop, ctypes.c_double(value)))

    def getnodevalues(self, prop: int) -> List[float]:
        """High-efficiency retrieval of a property for **all** nodes.

        Args:
            prop (int): Property code.

        Returns:
            List[float]: A list containing the values for all nodes.
        """
        count = self.getcount(EN_NODECOUNT)
        return [self.getnodevalue(i, prop) for i in range(1, count + 1)]

    def addnode(self, node_id: str, node_type: int) -> int:
        """Adds a new node to the network.

        Args:
            node_id (str): The ID for the new node.
            node_type (int): Node type (EN_JUNCTION, EN_RESERVOIR, EN_TANK).

        Returns:
            int: The index of the newly added node.
        """
        index = ctypes.c_int()
        self._check(_lib.EN_addnode(self.ph, ctypes.c_char_p(node_id.encode()), node_type, ctypes.byref(index)))
        return index.value

    def addlink(self, link_id: str, link_type: int, from_node: str, to_node: str) -> int:
        """Adds a new link to the network.

        Args:
            link_id (str): ID of the new link.
            link_type (int): Link type (EN_PIPE, EN_PUMP, etc.).
            from_node (str): ID of the start node.
            to_node (str): ID of the end node.

        Returns:
            int: The index of the newly added link.
        """
        index = ctypes.c_int()
        self._check(_lib.EN_addlink(self.ph, ctypes.c_char_p(link_id.encode()), link_type,
                                     ctypes.c_char_p(from_node.encode()),
                                     ctypes.c_char_p(to_node.encode()),
                                     ctypes.byref(index)))
        # If index was not updated (remains 0 or -1), try to fetch it
        if index.value <= 0:
            self._check(_lib.EN_getlinkindex(self.ph, ctypes.c_char_p(link_id.encode()), ctypes.byref(index)))
        return index.value

    # --- Link Properties (Double Precision) ---

    def getlinkindex(self, link_id: str) -> int:
        """Retrieves the internal index of a link by its ID.

        Args:
            link_id (str): The link ID string.

        Returns:
            int: The link index (1-based).
        """
        index = ctypes.c_int()
        self._check(_lib.EN_getlinkindex(self.ph, ctypes.c_char_p(link_id.encode()), ctypes.byref(index)))
        return index.value

    def getlinkid(self, index: int) -> str:
        """Retrieves the ID string of a link by its index.

        Args:
            index (int): The link index (1-based).

        Returns:
            str: The link ID.
        """
        id_buffer = ctypes.create_string_buffer(MAX_LABEL_LEN + 1)
        self._check(_lib.EN_getlinkid(self.ph, index, id_buffer))
        return id_buffer.value.decode()

    def getlinkvalue(self, index: int, prop: int) -> float:
        """Retrieves a double-precision property value for a link.

        Args:
            index (int): The link index (1-based).
            prop (int): Property code (e.g., EN_FLOW, EN_VELOCITY).

        Returns:
            float: The property value.
        """
        val = ctypes.c_double()
        self._check(_lib.EN_getlinkvalue(self.ph, index, prop, ctypes.byref(val)))
        return float(val.value)

    def setlinkvalue(self, index: int, prop: int, value: float):
        """Sets a property value for a link (Double Precision).

        Args:
            index (int): The link index (1-based).
            prop (int): Property code (e.g., EN_DIAMETER, EN_ROUGHNESS).
            value (float): The value to set.
        """
        self._check(_lib.EN_setlinkvalue(self.ph, index, prop, ctypes.c_double(value)))

    def getlinkvalues(self, prop: int) -> List[float]:
        """High-efficiency retrieval of a property for **all** links.

        Args:
            prop (int): Property code.

        Returns:
            List[float]: A list containing the values for all links.
        """
        count = self.getcount(EN_LINKCOUNT)
        return [self.getlinkvalue(i, prop) for i in range(1, count + 1)]

    def getcount(self, obj_type: int) -> int:
        """Retrieves the count of objects of a specific type.

        Args:
            obj_type (int): Object type code (e.g., EN_NODECOUNT, EN_LINKCOUNT).

        Returns:
            int: The number of objects.
        """
        count = ctypes.c_int()
        self._check(_lib.EN_getcount(self.ph, obj_type, ctypes.byref(count)))
        return count.value

    def setdemandmodel(self, model: int, pmin: float, preq: float, pexp: float):
        """Sets the demand model and its parameters (PDA vs DDA).

        Args:
            model (int): EN_DDA (0) or EN_PDA (1).
            pmin (float): Minimum pressure.
            preq (float): Required pressure.
            pexp (float): Pressure exponent.
        """
        self._check(_lib.EN_setdemandmodel(self.ph, model, 
                                           ctypes.c_double(pmin), 
                                           ctypes.c_double(preq), 
                                           ctypes.c_double(pexp)))

    # --- Demand Management (New in 2.2) ---

    def getnumdemands(self, node_index: int) -> int:
        """Retrieves the number of demand categories for a junction node.

        Args:
            node_index (int): The node index (1-based).

        Returns:
            int: The number of demand categories.
        """
        num = ctypes.c_int()
        self._check(_lib.EN_getnumdemands(self.ph, node_index, ctypes.byref(num)))
        return num.value

    def getbasedemand(self, node_index: int, demand_index: int) -> float:
        """Gets the double-precision base demand for a specific demand category.

        Args:
            node_index (int): The node index (1-based).
            demand_index (int): The demand category index (1-based).

        Returns:
            float: The base demand value.
        """
        val = ctypes.c_double()
        self._check(_lib.EN_getbasedemand(self.ph, node_index, demand_index, ctypes.byref(val)))
        return float(val.value)

    def setbasedemand(self, node_index: int, demand_index: int, value: float):
        """Sets the base demand for a specific demand category (Double Precision).

        Args:
            node_index (int): The node index (1-based).
            demand_index (int): The demand category index (1-based).
            value (float): The new base demand.
        """
        self._check(_lib.EN_setbasedemand(self.ph, node_index, demand_index, ctypes.c_double(value)))

    def adddemand(self, node_index: int, base_demand: float, pattern_name: str = '', demand_name: str = ''):
        """Appends a new demand category to a junction node (EPANET 2.2+).

        Args:
            node_index (int): The node index (1-based).
            base_demand (float): Base demand value.
            pattern_name (str, optional): Name of the time pattern.
            demand_name (str, optional): Descriptive name of the demand category.
        """
        self._check(_lib.EN_adddemand(self.ph, node_index, ctypes.c_double(base_demand),
                                      ctypes.c_char_p(pattern_name.encode()),
                                      ctypes.c_char_p(demand_name.encode())))

    def deletedemand(self, node_index: int, demand_index: int):
        """Removes a demand category from a junction node.

        Args:
            node_index (int): The node index (1-based).
            demand_index (int): The demand category index to delete.
        """
        self._check(_lib.EN_deletedemand(self.ph, node_index, demand_index))

    # --- Quality and Patterns ---

    def setqualtype(self, qual_type: int, chem_name: str = "", chem_units: str = "", trace_node: str = ""):
        """Sets the type of water quality analysis.

        Args:
            qual_type (int): EN_NONE, EN_CHEM, EN_AGE, or EN_TRACE.
            chem_name (str): Name of chemical.
            chem_units (str): Units of chemical.
            trace_node (str): ID of node to trace.
        """
        self._check(_lib.EN_setqualtype(self.ph, qual_type,
                                        ctypes.c_char_p(chem_name.encode()),
                                        ctypes.c_char_p(chem_units.encode()),
                                        ctypes.c_char_p(trace_node.encode())))

    def solveQ(self):
        """Runs a complete water quality simulation."""
        self._check(_lib.EN_solveQ(self.ph))

    def addpattern(self, pattern_id: str) -> int:
        """Adds a new time pattern.

        Args:
            pattern_id (str): ID of the new pattern.

        Returns:
            int: Index of the new pattern.
        """
        index = ctypes.c_int()
        self._check(_lib.EN_addpattern(self.ph, ctypes.c_char_p(pattern_id.encode()), ctypes.byref(index)))
        # If index was not updated (remains 0 or -1), try to fetch it
        if index.value <= 0:
            self._check(_lib.EN_getpatternindex(self.ph, ctypes.c_char_p(pattern_id.encode()), ctypes.byref(index)))
        return index.value

    def setpattern(self, index: int, factors: List[float]):
        """Sets all multipliers for a pattern.

        Args:
            index (int): Pattern index.
            factors (List[float]): Multipliers.
        """
        count = len(factors)
        cfactors = (ctypes.c_double * count)(*factors)
        self._check(_lib.EN_setpattern(self.ph, index, cfactors, count))

    def getpatternvalue(self, index: int, period: int) -> float:
        """Retrieves the multiplier for a pattern period.

        Args:
            index (int): Pattern index.
            period (int): Period index (1-based).

        Returns:
            float: Multiplier value.
        """
        val = ctypes.c_double()
        self._check(_lib.EN_getpatternvalue(self.ph, index, period, ctypes.byref(val)))
        return float(val.value)

    # --- Controls and Statistics ---

    def addcontrol(self, type: int, link: int, setting: float, node: int, level: float) -> int:
        """Adds a new simple control.

        Args:
            type (int): Control type (EN_LOWLEVEL, EN_HILEVEL, EN_TIMER, EN_TIMEOFDAY).
            link (int): Index of the controlled link.
            setting (float): Control setting (0/1 for open/closed, or valve setting).
            node (int): Index of the controlling node (0 for timer/timeofday).
            level (float): Control trigger level/time.

        Returns:
            int: The index of the new control.
        """
        idx = ctypes.c_int()
        self._check(_lib.EN_addcontrol(self.ph, type, link, ctypes.c_double(setting), node, ctypes.c_double(level), ctypes.byref(idx)))
        return idx.value

    def getcontrol(self, index: int) -> Tuple[int, int, float, int, float]:
        """Retrieves parameters of a simple control.

        Args:
            index (int): Control index.

        Returns:
            Tuple: (type, link, setting, node, level).
        """
        ctype = ctypes.c_int()
        clink = ctypes.c_int()
        cset = ctypes.c_double()
        cnode = ctypes.c_int()
        clev = ctypes.c_double()
        self._check(_lib.EN_getcontrol(self.ph, index, ctypes.byref(ctype), ctypes.byref(clink), ctypes.byref(cset), ctypes.byref(cnode), ctypes.byref(clev)))
        return ctype.value, clink.value, float(cset.value), cnode.value, float(clev.value)

    def setcontrol(self, index: int, type: int, link: int, setting: float, node: int, level: float):
        """Modifies an existing simple control."""
        self._check(_lib.EN_setcontrol(self.ph, index, type, link, ctypes.c_double(setting), node, ctypes.c_double(level)))

    def deletecontrol(self, index: int):
        """Deletes a simple control."""
        self._check(_lib.EN_deletecontrol(self.ph, index))

    def getstatistic(self, type_code: int) -> float:
        """Retrieves a simulation statistic (iterations, relative error, etc.)."""
        val = ctypes.c_double()
        self._check(_lib.EN_getstatistic(self.ph, type_code, ctypes.byref(val)))
        return float(val.value)

    def getoption(self, type_code: int) -> float:
        """Retrieves a project option (accuracy, trials, etc.)."""
        val = ctypes.c_double()
        self._check(_lib.EN_getoption(self.ph, type_code, ctypes.byref(val)))
        return float(val.value)

    def setoption(self, type_code: int, value: float):
        """Sets a project option."""
        self._check(_lib.EN_setoption(self.ph, type_code, ctypes.c_double(value)))

    def gettitle(self) -> Tuple[str, str, str]:
        """Retrieves the three title lines of the project."""
        l1 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
        l2 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
        l3 = ctypes.create_string_buffer(MAX_TITLE_LEN + 1)
        self._check(_lib.EN_gettitle(self.ph, l1, l2, l3))
        return l1.value.decode(), l2.value.decode(), l3.value.decode()

    def settitle(self, line1: str = "", line2: str = "", line3: str = ""):
        """Sets the three title lines of the project."""
        self._check(_lib.EN_settitle(self.ph, line1.encode(), line2.encode(), line3.encode()))
