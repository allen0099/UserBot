import logging
import sys
from configparser import ConfigParser
from pathlib import Path

from bot.types.Config import Config

log: logging = logging.getLogger(__name__)


def get_configs() -> Config:
    parser: ConfigParser = ConfigParser()
    parser.read(str(Path(sys.argv[0]).parent / "config.ini"))

    return Config(
        log_channel=parser.get("custom", "log_channel")
    )
