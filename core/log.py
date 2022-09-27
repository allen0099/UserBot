import logging
import os
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler
from typing import Optional

import coloredlogs

from core import settings

# ---------------------------------------------------------------------------
#   Global Variables
# ---------------------------------------------------------------------------

LEVEL: int = logging.INFO

if settings.DEBUG:
    LEVEL: int = logging.DEBUG

# ---------------------------------------------------------------------------
#   Prepare folders
# ---------------------------------------------------------------------------

if not os.path.exists("logs"):
    os.mkdir("logs")
    print("Folder logs created.")

if not os.path.exists("logs/bot"):
    os.mkdir("logs/bot")
    print("Folder logs/bot created.")

if not os.path.exists("logs/third"):
    os.mkdir("logs/third")
    print("Folder logs/third created.")


# ---------------------------------------------------------------------------
#   Initialize handlers
# ---------------------------------------------------------------------------


class Handlers:
    READ_FORMATTER: str = (
        "%(asctime)s %(name)s[%(process)d:%(thread)d] %(levelname)s %(message)s"
    )

    BASIC_FORMATTER: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    if not settings.DEBUG:
        # 設定預設 logging 等級
        MAIN_FORMATTER: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(name)s[%(process)d:%(thread)d] - "
            "%(levelname)s - %(message)s"
        )

    else:
        MAIN_FORMATTER: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(processName)s(%(process)d):%(threadName)s(%(thread)d) - "
            "[%(levelname)8s] %(name)s:%(lineno)d - %(message)s"
        )

    EVENT_HANDLER: TimedRotatingFileHandler = TimedRotatingFileHandler(
        "logs/bot/events.log", when="midnight", encoding="utf-8"
    )
    EVENT_HANDLER.setFormatter(BASIC_FORMATTER)

    MAIN_HANDLER: TimedRotatingFileHandler = TimedRotatingFileHandler(
        "logs/bot/bot.log", when="midnight", encoding="utf-8"
    )
    MAIN_HANDLER.setFormatter(MAIN_FORMATTER)

    BASIC_HANDLERS: dict[str, BaseRotatingHandler] = {}

    @classmethod
    def get_handler(cls, name: str, bot: bool = False):
        if cls.BASIC_HANDLERS.get(name):
            return cls.BASIC_HANDLERS[name]

        directory: str = "bot" if bot else "third"
        new_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
            f"logs/{directory}/{name}.log", when="midnight", encoding="utf-8"
        )
        new_handler.setFormatter(cls.BASIC_FORMATTER)

        cls.BASIC_HANDLERS[name] = new_handler
        return cls.BASIC_HANDLERS[name]


# ---------------------------------------------------------------------------
#   Usable Loggers
# ---------------------------------------------------------------------------


# Basic singleton logger
class BasicLogger:
    _instance: Optional["BasicLogger"] = None
    _initialized: bool = False

    def __init__(self, name: str, detail: bool = False):
        if self._initialized:
            return

        self.logger: logging.Logger = logging.getLogger(name)

        if detail:
            self.level: int = logging.INFO

        else:
            self.level: int = logging.WARNING

        self.logger.addHandler(Handlers.get_handler(name))
        self.logger.setLevel(self.level)
        coloredlogs.install(
            logger=self.logger, level=self.level, fmt=Handlers.READ_FORMATTER
        )

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class PyrogramLogger(BasicLogger):
    def __init__(self, detail: bool = False):
        super().__init__("pyrogram", detail)


class SQLAlchemyEngineLogger(BasicLogger):
    def __init__(self, detail: bool = False):
        """
        Controls SQL echoing.
        Set to logging.INFO for SQL query output, logging.DEBUG for query + result set output.
        These settings are equivalent to echo=True and echo="debug" on create_engine.echo, respectively.
        """
        super().__init__("sqlalchemy.engine", detail)


class SQLAlchemyPoolLogger(BasicLogger):
    def __init__(self, detail: bool = False):
        """
        Controls connection pool logging.
        Set to logging.INFO to log connection invalidation and recycle events;
        set to logging.DEBUG to additionally log all pool checkins and checkouts.
        These settings are equivalent to pool_echo=True and pool_echo="debug" on create_engine.echo_pool, respectively.
        """
        super().__init__("sqlalchemy.pool", detail)


class SQLAlchemyDialectsLogger(BasicLogger):
    def __init__(self, detail: bool = False):
        """
        Controls custom logging for SQL dialects,
        to the extend that logging is used within specific dialects, which is generally minimal.
        """
        super().__init__("sqlalchemy.dialects", detail)


class SQLAlchemyORMLogger(BasicLogger):
    def __init__(self, detail: bool = False):
        """
        Controls logging of various ORM functions to the extent that logging is used within the ORM,
        which is generally minimal.
        Set to logging.INFO to log some top-level information on mapper configurations.
        """
        super().__init__("sqlalchemy.orm", detail)


def event_logger(name: str) -> logging.Logger:
    """
    For those you don't want to see them in console.

    Args:
        name:

    Returns:

    """
    logger: logging.Logger = logging.Logger(f"event.{name}")
    logger.addHandler(Handlers.EVENT_HANDLER)
    logger.setLevel(LEVEL)
    logger.propagate = False

    return logger


def main_logger(name: str) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    logger.addHandler(Handlers.MAIN_HANDLER)
    logger.setLevel(LEVEL)
    logger.propagate = False

    coloredlogs.install(logger=logger, level=LEVEL, fmt=Handlers.READ_FORMATTER)
    return logger
