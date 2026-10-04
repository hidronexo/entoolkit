"""
EnToolkit: A Pythonic wrapper for the EPANET 2.2 hydraulic simulation engine.

This package provides two ways to interact with EPANET:
1.  **Modern Handle-Based API** (in `entoolkit.toolkit`): 
    The `EPANETProject` class provides a thread-safe, double-precision interface 
    capable of managing multiple projects simultaneously.
2.  **Legacy Global-State API** (in `entoolkit.legacy`): 
    A direct mapping of the traditional EPANET toolkit functions for 
    quick scripts and backwards compatibility.

Example (Modern API):
    >>> from entoolkit import EPANETProject
    >>> proj = EPANETProject()
    >>> proj.open("network.inp")
    >>> proj.solveH()
    >>> proj.close()

Example (Legacy API):
    >>> from entoolkit import legacy
    >>> legacy.ENopen("network.inp")
    >>> legacy.ENsolveH()
    >>> legacy.ENclose()
"""
from . import constants, legacy, toolkit
from .constants import *
from .logger import init_logger
from .toolkit import EPANETProject

__version__ = "0.0.15"

# Initialize logging for the toolkit
init_logger()
