"""Qt desktop entry point. Boots the host on a background thread."""

from __future__ import annotations

import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

from sfxgen.config.settings import load_settings
from sfxgen.core.host import PluginHost
from sfxgen.services.model_service import ModelService
from sfxgen.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ai-sound-effect-generator")

    settings = load_settings()
    host = PluginHost.from_settings(settings)
    models = ModelService(settings=settings)

    window = MainWindow(host=host, models=models)
    window.show()
    logger.info("desktop up — {} plugins, {} models", len(host.registry), models.count())
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())