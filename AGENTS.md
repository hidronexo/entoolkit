# entoolkit — agent instructions

Follow the central policy in `hidronexo-meta/AGENTS.md`.

- Visibility and license: public, `GPL-2.0-or-later` (see `repos.toml` in `hidronexo-meta`). Authors, commits, and public metadata use `HIDRONEXO <opensource@hidronexo.com>`.
- Core paths (no UI imports): `entoolkit/toolkit.py`, `entoolkit/legacy.py`, `entoolkit/constants.py`.
- Bundled EPANET binaries live in `entoolkit/epanet/`; their licenses are reproduced in `THIRD_PARTY_LICENSES`. Update that file whenever a binary changes.
- `entoolkit` must not depend on any other HIDRONEXO project at runtime.
- Keep the version in `pyproject.toml` as the single source; `entoolkit/__init__.py` mirrors it for `__version__`.
