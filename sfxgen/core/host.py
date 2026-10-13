"""PluginHost — the runtime that loads plugins and dispatches renders."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger

from sfxgen.config.settings import Settings
from sfxgen.contracts.plugin import PluginContext, RenderRequest, RenderResult, SfxPlugin
from sfxgen.core.registry import PluginRegistry
from sfxgen.utils.devices import pick_device


class PluginHost:
    """Owns the registry, the plugin instances, and the render context."""

    def __init__(self, registry: PluginRegistry, settings: Settings) -> None:
        self.registry = registry
        self.settings = settings
        self._instances: dict[str, SfxPlugin] = {}
        self._device = pick_device(settings.prefer_gpu)

    @classmethod
    def from_settings(cls, settings: Settings) -> "PluginHost":
        registry = PluginRegistry()
        registry.discover(settings.plugin_dirs())
        host = cls(registry=registry, settings=settings)
        host.load_all()
        return host

    def load_all(self) -> None:
        for manifest in self.registry.list_manifests():
            try:
                self._instances[manifest.id] = self.registry.instantiate(manifest.id)
                logger.info("loaded plugin {} v{}", manifest.id, manifest.version)
            except Exception as exc:  # a broken plugin must not kill the host
                logger.error("failed to load {}: {}", manifest.id, exc)

    def warmup(self) -> None:
        ctx = self._make_context()
        for pid, plugin in self._instances.items():
            try:
                plugin.warmup(ctx)
            except Exception as exc:
                logger.warning("warmup failed for {}: {}", pid, exc)

    def render(self, plugin_id: str, request: RenderRequest) -> RenderResult:
        plugin = self._instances.get(plugin_id)
        if plugin is None:
            raise KeyError(f"plugin not loaded: {plugin_id}")
        return plugin.render(request, self._make_context())

    def shutdown(self) -> None:
        for pid, plugin in self._instances.items():
            try:
                plugin.teardown()
            except Exception as exc:
                logger.warning("teardown failed for {}: {}", pid, exc)

    def _make_context(self) -> PluginContext:
        return PluginContext(
            cache_dir=self.settings.cache_dir,
            device=self._device,
            logger=logger,
            rng=np.random.default_rng(self.settings.seed if self.settings.seed >= 0 else None),
        )