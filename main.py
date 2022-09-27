import logging

from bot import Bot
from core.log import (
    main_logger,
    PyrogramLogger,
    SQLAlchemyEngineLogger,
    SQLAlchemyORMLogger,
    SQLAlchemyDialectsLogger,
    SQLAlchemyPoolLogger,
)

log: logging.Logger = main_logger(__name__)
pg_log: logging.Logger = PyrogramLogger().logger

sa_engine_log: logging.Logger = SQLAlchemyEngineLogger().logger
sa_dialects_log: logging.Logger = SQLAlchemyDialectsLogger().logger
sa_orm_log: logging.Logger = SQLAlchemyORMLogger().logger
sa_pool_log: logging.Logger = SQLAlchemyPoolLogger().logger

if __name__ == "__main__":
    bot: Bot = Bot()
    bot.run()

    log.info("Bye!")
    logging.shutdown()
