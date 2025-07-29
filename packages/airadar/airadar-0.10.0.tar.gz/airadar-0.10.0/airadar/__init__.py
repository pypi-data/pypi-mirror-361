"""Radar Tool"""

from __future__ import annotations
from ._version import __version__

from pathlib import Path

import logging
import logging.config
from logging.handlers import RotatingFileHandler

from airadar import typing as radar_types
from airadar.tracking.decorators import pipeline
from airadar.extractors.dependency import Extractor
from airadar.extractors.dependency import PackageDependencyType
from airadar.extractors.dependency import DependencyExtractor
from airadar.radar import Radar, RadarPipeline
from airadar.tracking.fluent import log_model, log_deployment, active_run

from airadar.utils.config import airadar_configs, ConfigKeys

__all__ = [
    "radar_types",
    "pipeline",
    "Extractor",
    "Radar",
    "RadarPipeline",
    "PackageDependencyType",
    "DependencyExtractor",
    "log_model",
    "log_deployment",
    "active_run",
    "__version__",
]


def setup_logging() -> None:
    config_file = Path().resolve().joinpath("logging.conf")

    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARN": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    if config_file.exists() and config_file.is_file():
        logging.config.fileConfig(config_file, disable_existing_loggers=False)
    else:
        log_level_config = airadar_configs.get_value(ConfigKeys.AIRADAR_LOG_LEVEL)
        if not log_level_config:
            log_level_config = "INFO"
        else:
            log_level_config = str(log_level_config)

        log_level = log_levels.get(log_level_config, logging.INFO)

        rfh = RotatingFileHandler("radar.log", maxBytes=1 * 1024 * 1024, backupCount=3)
        rfh.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s loglevel=%(levelname)-6s logger=%(name)s %(funcName)s() L%(lineno)-4d %(message)s"
        )
        rfh.setFormatter(formatter)

        logger = logging.getLogger("airadar")
        logger.setLevel(log_level)
        logger.addHandler(rfh)


setup_logging()
