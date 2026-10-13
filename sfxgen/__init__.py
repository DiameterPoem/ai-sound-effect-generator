"""ai-sound-effect-generator — plugin-host AI sound effect generator."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ai-sound-effect-generator")
except PackageNotFoundError:  # editable install without metadata
    __version__ = "0.9.4"

__all__ = ["__version__"]