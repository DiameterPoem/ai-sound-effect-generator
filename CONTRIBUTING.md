# Contributing to ai-sound-effect-generator

Thanks for wanting to help build the plugin host. This repo is a Windows-first
desktop tool that turns text prompts and sample libraries into sound effects
using diffusion, granular synthesis, and morph engines. Everything runs
through the plugin host — if you want a new synthesis backend, you write a
plugin, not a fork.

## Layout

```
sfxgen/
  bootstrap/      entry points (CLI, GUI, first-run)
  core/           host runtime, pipeline, device management
  plugins/        bundled plugins (each self-contained)
  handlers/       request handlers (render, batch, preview, export)
  services/       long-lived services (model loader, cache, audio bus)
  models/         pydantic schemas + model registry types
  utils/          audio IO, dsp helpers, logging, paths
  config/         default configs + user config merge
  contracts/      plugin protocol + shared interfaces
```

## Writing a plugin

1. Subclass `sfxgen.contracts.plugin.SfxPlugin`.
2. Implement `manifest()` and `render(request, ctx) -> RenderResult`.
3. Register via `pyproject.toml` entry point under `sfxgen.plugins`.
4. Add a test under `tests/plugins/`.

Plugins must be pure: no globals, no direct file writes, no network. All
state comes from `PluginContext`.

## Running locally

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
sfxgen --help
sfxgen plugins list
pytest
```

## Style

- `ruff` for lint + format, line length 100.
- `mypy --strict` on `sfxgen/`. Type every public function.
- No bare `except`. No silent failures. Log with `loguru`, never `print`.
- Audio buffers are always `np.ndarray[float32]` shaped `(channels, samples)`.
- Sample rate is explicit — never assume 44.1k.

## PRs

- One feature per PR. Keep the diff under ~400 lines.
- Update `docs/plugins.md` if you touch the contract.
- Add a changelog line in `CHANGELOG.md`.
- CI runs ruff, mypy, pytest on Windows + Linux.

## Reporting bugs

Open an issue with: OS build, Python version, `sfxgen --version`, the plugin
ID, and the exact prompt or sample you used. Attach the log from
`%LOCALAPPDATA%\sfxgen\logs\`.