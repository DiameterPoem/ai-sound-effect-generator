"""CLI entry point. Wires config -> host -> handler and dispatches."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console

from sfxgen import __version__
from sfxgen.config.settings import load_settings
from sfxgen.core.host import PluginHost
from sfxgen.handlers.render_handler import RenderHandler
from sfxgen.utils.logging import configure_logging

app = typer.Typer(
    name="sfxgen",
    help="AI sound effect generator — plugin-host CLI.",
    no_args_is_help=True,
    add_completion=False,
)
plugins_app = typer.Typer(help="Inspect and manage plugins.")
app.add_typer(plugins_app, name="plugins")
console = Console()


@app.callback()
def _root(
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    configure_logging(level="DEBUG" if verbose else "INFO")


@app.command()
def version() -> None:
    """Print the version."""
    console.print(f"sfxgen {__version__}")


@app.command()
def render(
    prompt: Annotated[str, typer.Argument(help="Text prompt, e.g. 'metallic door slam'")],
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("renders/out.wav"),
    plugin: Annotated[str, typer.Option("--plugin", "-p")] = "diffusion-oneshot",
    duration: Annotated[float, typer.Option("--duration", "-d")] = 2.0,
    seed: Annotated[int, typer.Option("--seed")] = -1,
) -> None:
    """Render a single sound effect from a prompt."""
    settings = load_settings()
    host = PluginHost.from_settings(settings)
    handler = RenderHandler(host)
    result = handler.render(prompt=prompt, plugin_id=plugin, duration=duration, seed=seed, out=out)
    console.print(f"[green]rendered[/] {result.path} ({result.duration:.2f}s @ {result.sample_rate} Hz)")


@plugins_app.command("list")
def plugins_list() -> None:
    """List every plugin the host can see."""
    settings = load_settings()
    host = PluginHost.from_settings(settings)
    for manifest in host.registry.list_manifests():
        console.print(f"[cyan]{manifest.id}[/]  {manifest.name}  v{manifest.version}")


def main() -> int:
    try:
        app()
    except Exception as exc:  # top-level guard so we log instead of traceback-dumping
        logger.exception("fatal: {}", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())