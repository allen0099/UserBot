import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import registry, scoped_session, sessionmaker
from sqlalchemy.orm.decl_api import declarative_base

log: logging.Logger = logging.getLogger(__name__)


class Database:
    engine: Engine = create_engine(os.getenv("SQLITE_URI"), future=True)

    mapper_registry: registry = registry()
    base: declarative_base = mapper_registry.generate_base()
    metadata = base.metadata

    session = scoped_session(sessionmaker(engine))

    def init(self):
        self.metadata.create_all(self.engine)
        try:
            self.session()
        except Exception as e:
            log.exception(f'[Database] Session started failed due to {e}')
        log.info("[Database] Connection successful, session started.")


db: Database = Database()
db.init()

from . import privilege
