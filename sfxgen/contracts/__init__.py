"""Shared contracts between host, plugins, and handlers."""

from sfxgen.contracts.plugin import PluginContext, PluginManifest, RenderRequest, RenderResult, SfxPlugin

__all__ = ["SfxPlugin", "PluginManifest", "PluginContext", "RenderRequest", "RenderResult"]