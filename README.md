# entoolkit

Python extension for the **EPANET 2.2** Programmer Toolkit.

`entoolkit` provides a Pythonic wrapper around the EPANET hydraulic simulation engine. It includes two distinct APIs to suit different needs:
1.  **Modern Handle-Based API (`entoolkit.toolkit`)**: A thread-safe, high-precision interface (64-bit double) that allows managing multiple projects simultaneously. **(Recommended)**
2.  **Legacy Global-State API (`entoolkit.legacy`)**: A direct mapping of the traditional EPANET functions for quick scripts and backwards compatibility.

---

## Installation

Currently, you can install the package by cloning the repository and installing it in editable mode, or via pip (if published):

```bash
pip install -e .
```

The package comes pre-bundled with 64-bit binaries for **Windows**, **Linux**, and **macOS** (Intel & Apple Silicon).

---

## Quick Start

### 1. Modern API (Recommended)
This API uses the new EPANET 2.2 handle system, supports thread-safe operations, and utilizes **double precision** (`double`) for higher numerical accuracy.

```python
from entoolkit import EPANETProject, EN_PRESSURE

# Create a new project instance
proj = EPANETProject()

# Open a network file
proj.open("networks/Net1.inp", "report.rpt", "out.bin")

# Solve hydraulics
proj.solveH()

# Retrieve pressures for all nodes efficiently
pressures = proj.getnodevalues(EN_PRESSURE)
print(f"Nodes count: {len(pressures)}")

# Close and free memory
proj.close()
proj.delete()
```

### 2. Legacy API
Provides a familiar environment for those used to the classic EPANET C API. It operates on a single global state.

```python
from entoolkit import legacy

# Open a network
legacy.ENopen("networks/Net1.inp", "report.rpt")

# Solve hydraulics
legacy.ENsolveH()

# Retrieve a single value
p_node_1 = legacy.ENgetnodevalue(1, legacy.EN_PRESSURE)

# Close project
legacy.ENclose()
```

## Documentation

The library is fully documented using "Pythonic" docstrings (Google Style). You can access detailed information about any function, including its parameters and return values, directly from the Python REPL:

```python
from entoolkit import EPANETProject
help(EPANETProject.open)

from entoolkit import legacy
help(legacy.ENaddnode)
```

---

## What's New in 2.2
- **Multiple Demands**: Support for multiple demand categories per junction.
- **Advanced Controls**: New rule-based control functions.
- **Pressure Dependent Demands (PDA)**: Direct support for PDA simulation models.
- **High Precision**: The handle-based API uses 64-bit doubles for all physical properties.

---

## Running Tests
The package includes a comprehensive test suite in `run_tests.py`.

```bash
python run_tests.py
```

---

## Origin and Credits

The binaries included in this package are derived from:
1. **Open Water Analytics (OWA) EPANET**: The official community-driven EPANET 2.2 engine. [GitHub Repo](https://github.com/OpenWaterAnalytics/EPANET)
2. **WNTR (US EPA)**: Some platform-specific binaries and network examples were adapted from the Water Network Tool for Resilience. [WNTR GitHub](https://github.com/USEPA/WNTR)

### Citation
If you use this toolkit in your research, please cite the original EPANET engine:
> Rossman, L. A. (2000). EPANET 2: users manual. U.S. Environmental Protection Agency, Cincinnati, OH, EPA/600/R-00/057.

And the OWA community for the 2.2 upgrade:
> Open Water Analytics. (2020). EPANET 2.2.0. https://github.com/OpenWaterAnalytics/EPANET

---

## License

The `entoolkit` wrapper is licensed under the **GNU General Public License v2 or later (GPL-2.0-or-later)**.
Bundled EPANET (MIT) and WNTR (BSD-3-Clause) binaries keep their own licenses, which are compatible with the GPL for redistribution. Their notices are reproduced in `THIRD_PARTY_LICENSES`.

---

## Documentation
- [Official EPANET 2.2 Manual](https://usepa.github.io/EPANET2.2/)
- [EPANET 2.2 Toolkit API Reference](https://wateranalytics.org/EPANET/topics.html)
