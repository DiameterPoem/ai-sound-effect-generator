"""Plugin discovery + instantiation via importlib.metadata entry points."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from pathlib import Path

from loguru import logger

from sfxgen.contracts.plugin import PluginManifest, SfxPlugin

GROUP = "sfxgen.plugins"


class PluginRegistry:
    """Reads entry points, keeps a manifest index, instantiates on demand."""

    def __init__(self) -> None:
        self._manifests: dict[str, PluginManifest] = {}
        self._entry_points: dict[str, EntryPoint] = {}

    def discover(self, extra_dirs: list[Path] | None = None) -> None:
        for ep in entry_points(group=GROUP):
            try:
                plugin_cls = ep.load()
                instance: SfxPlugin = plugin_cls()
                manifest = instance.manifest()
            except Exception as exc:
                logger.error("skipping broken entry point {}: {}", ep.name, exc)
                continue
            self._manifests[manifest.id] = manifest
            self._entry_points[manifest.id] = ep
            logger.debug("discovered {} from {}", manifest.id, ep.value)

        for extra in extra_dirs or []:
            self._discover_dir(extra)

    def _discover_dir(self, directory: Path) -> None:
        if not directory.is_dir():
            return
        for child in sorted(directory.iterdir()):
            if child.suffix == ".sfxplugin" and child.is_dir():
                logger.info("external plugin dir: {}", child)

    def list_manifests(self) -> list[PluginManifest]:
        return sorted(self._manifests.values(), key=lambda m: m.id)

    def instantiate(self, plugin_id: str) -> SfxPlugin:
        ep = self._entry_points.get(plugin_id)
        if ep is None:
            raise KeyError(f"unknown plugin: {plugin_id}")
        return ep.load()()

    def __len__(self) -> int:
        return len(self._manifests)