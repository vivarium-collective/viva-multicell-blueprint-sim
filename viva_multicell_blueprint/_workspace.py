"""Locate the investigation workspace at runtime (post simulator/workspace split).

This package used to live *inside* the investigation workspace repo, so modules
reached workspace files (``workspace/blueprints/*.yaml``, ``workspace/scenes/*``,
the ``.pbg/schemas`` dir, …) with ``Path(__file__).resolve().parents[2]``. Since
the simulator was split into its own distribution, the package is installed in
``site-packages`` and ``__file__`` no longer sits above the workspace — those
reaches resolve to the wrong place.

Resolve the workspace from the runtime *working directory* instead, which is the
investigation repo root when the dashboard, a study run, or the test suite runs:

* honor ``$WORKSPACE_DIR`` when it points at a dir holding ``workspace.yaml``;
* else walk up from the current working directory looking for ``workspace.yaml``;
* else fall back to the current working directory.

Package-INTERNAL data (schemas, fixtures shipped in the wheel) must NOT use this
helper — those are resolved relative to ``__file__`` and ship with the package.
"""
from __future__ import annotations

import os
from pathlib import Path


def workspace_root() -> Path:
    """Return the investigation workspace root (the dir that holds workspace.yaml).

    Best-effort and cwd-anchored; never raises. Falls back to the current
    working directory when no ``workspace.yaml`` is found, so a caller that joins
    ``"workspace"`` onto it still produces a sensible (if absent) path rather than
    pointing into site-packages.
    """
    env = os.environ.get("WORKSPACE_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "workspace.yaml").is_file():
            return p
    start = Path.cwd().resolve()
    for d in (start, *start.parents):
        if (d / "workspace.yaml").is_file():
            return d
    return start
