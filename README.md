# viva-multicell-blueprint-sim

The **simulator** for the viva-multicell-blueprint research program: a
backend-neutral multicellular *blueprint* engine and the process-bigraph
composites, processes, mechanism modules, model-format adapters, and
visualization code that run it. Extracted from
[`viva-multicell-blueprint`](https://github.com/vivarium-collective/viva-multicell-blueprint)
so the investigation workspace (studies + investigations) can pin the simulator
by a git tag and evolve independently of it.

Installs as the **`viva_multicell_blueprint`** package (the import name is
unchanged, so study `composite:` dotted paths such as
`viva_multicell_blueprint.composites.sego.sego` resolve exactly as before).

## What's here

A single biological *blueprint* (cell types, adhesion, fields, rules, division,
subcellular modules) compiles onto several mechanical backends side by side:

- **CPM** — Cellular Potts (`viva-cpm`, Rust core)
- **vertex** — tissue vertex model (`vivarium-tyssue` → `tyssue`)
- **center-based** — pymunk rigid-body physics (`viva-munk`)
- **particle** — Smoldyn bounded particles (optional `[particles]` extra)

Plus a model-format layer with pluggable **subcellular** adapters — ODE
(`viva-tellurium` / RoadRunner), Boolean (MaBoSS / `cmaboss`), and particle
(Smoldyn) — and a rule grammar (`viva-grammar`), composed through
process-bigraph.

## Install

```bash
# core simulator (all mechanical backends + ODE/Boolean subcellular)
uv pip install "viva-multicell-blueprint-sim @ git+https://github.com/vivarium-collective/viva-multicell-blueprint-sim.git@0.1.0"

# with the Smoldyn particle engine
uv pip install "viva-multicell-blueprint-sim[particles] @ git+...@0.1.0"
```

`import viva_multicell_blueprint` pulls **zero** investigation framework. The
workbench dashboard, superpowers composite tooling, and discovery-engine
evaluator plugins are an optional `[workspace]` extra, needed only when the
simulator is driven *from* the investigation workspace.

## Tests

```bash
uv pip install -e ".[dev]"
pytest
```

The test suite here is the simulator's **unit** coverage (mechanism, backends,
adapters, compile, viz, metrics). The workspace-integration tests (studies that
run blueprints committed under `workspace/`, the Blueprint Studio served assets,
the canonical SEgO 2022 example blueprints) live with the investigation workspace
in `viva-multicell-blueprint`, since they read workspace content this package no
longer ships.

## Versioning

Plain-version tags: the git tag equals the `pyproject` version equals the study
`simulator.ref` (e.g. `0.1.0`, no `v` prefix).
