"""JSON-schema validation + BP-01 structured diagnostics for blueprint documents."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

from .canonical import canonical_violations

# The blueprint JSON-schema ships WITH the package (it defines the package's own
# blueprint format). It used to be read from the workspace's `.pbg/schemas/` dir,
# but post simulator/workspace split the package is installed externally, so it
# carries its own copy under `blueprint/schemas/` (bundled into the wheel). A
# workspace `.pbg/schemas/` copy, when present, is preferred so an investigation
# can override the schema without re-releasing the simulator.
_PKG_SCHEMA = Path(__file__).resolve().parent / "schemas" / "multicell_blueprint.schema.json"
_WS_SCHEMA = Path.cwd() / ".pbg" / "schemas" / "multicell_blueprint.schema.json"
SCHEMA_PATH = _WS_SCHEMA if _WS_SCHEMA.is_file() else _PKG_SCHEMA


@lru_cache(maxsize=1)
def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _branch_validator(name: str) -> Draft202012Validator:
    """Validator for one oneOf branch (flat_v1 / sectioned_v2), keeping $defs.

    Validating the matching branch directly (instead of the top-level oneOf)
    keeps error messages specific, e.g. ``domain`` is required.
    """
    schema = _schema()
    return Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]})


class _Dispatch:
    """Pick the schema branch by document shape; errors come from that branch."""

    def iter_errors(self, doc):
        v2 = isinstance(doc, dict) and ("initial_conditions" in doc or "model_definition" in doc)
        return _branch_validator("sectioned_v2" if v2 else "flat_v1").iter_errors(doc)


def _validator() -> _Dispatch:
    return _Dispatch()


def validate(doc) -> list[str]:
    """Return a list of human-readable schema ERRORS; empty means schema-valid.

    Back-compat surface (errors only). New code should prefer
    :func:`validate_blueprint`, which also returns warnings.
    """
    errs = sorted(_validator().iter_errors(doc), key=lambda e: list(map(str, e.path)))
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in errs]


def validate_blueprint(doc) -> list[dict]:
    """Return structured diagnostics ``[{severity, path, message}]`` (BP-01).

    - ``error``   — JSON-schema violations (the blueprint will not compile reliably);
    - ``warning`` — the canonical contract: a missing ``blueprint_version`` and any
      backend/run parameter found inside the canonical biological blueprint.

    An empty list means schema-valid AND contract-clean. Errors and warnings are
    both surfaced so the validator exposes problems, not just a success badge.
    """
    diags: list[dict] = []
    for e in sorted(_validator().iter_errors(doc), key=lambda e: list(map(str, e.path))):
        diags.append({
            "severity": "error",
            "path": "/".join(map(str, e.absolute_path)) or "<root>",
            "message": e.message,
        })
    if isinstance(doc, dict):
        if not doc.get("blueprint_version"):
            diags.append({
                "severity": "warning",
                "path": "blueprint_version",
                "message": ("no blueprint_version declared; set it so the canonical "
                            "schema version is auditable (BP-01)."),
            })
        diags.extend(canonical_violations(doc))
    return diags
