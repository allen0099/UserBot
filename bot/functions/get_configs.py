import sys
from configparser import ConfigParser
from pathlib import Path

from bot.types.Config import Config


def get_configs() -> Config:
    parser: ConfigParser = ConfigParser()
    parser.read(str(Path(sys.argv[0]).parent / "config.ini"))

    return Config(
        log_channel=parser.get("custom", "log_channel")
    )
