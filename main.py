import logging

from bot import Bot
from core.log import (
    PyrogramLogger,
    SQLAlchemyDialectsLogger,
    SQLAlchemyEngineLogger,
    SQLAlchemyORMLogger,
    SQLAlchemyPoolLogger,
    main_logger,
)
from database import alembic_upgrade, get_current, get_head, need_upgrade

log: logging.Logger = main_logger(__name__)

pyrogram_log: logging.Logger = PyrogramLogger().logger
sa_engine_log: logging.Logger = SQLAlchemyEngineLogger().logger
sa_dialects_log: logging.Logger = SQLAlchemyDialectsLogger().logger
sa_orm_log: logging.Logger = SQLAlchemyORMLogger().logger
sa_pool_log: logging.Logger = SQLAlchemyPoolLogger().logger

if __name__ == "__main__":
    log.info("Checking database status!")
    if need_upgrade():
        log.info(f"Current version: {get_current()}")
        log.info(f"Heads: {get_head()}")
        log.info("Upgrading database!")
        alembic_upgrade()

    bot: Bot = Bot()
    bot.run()

    log.info("Bye!")
    logging.shutdown()
