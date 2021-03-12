import logging
import os

# noinspection PyProtectedMember
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session, sessionmaker

log: logging.Logger = logging.getLogger(__name__)


class Database:
    base: DeclarativeMeta = declarative_base()

    def __init__(self):
        self._host: str = os.getenv("DB_HOST")
        self._db_name: str = os.getenv("DB_DATABASE")
        self._username: str = os.getenv("DB_USERNAME")
        self._password: str = os.getenv("DB_PASSWORD")
        self._connect_string: str = f"mysql+pymysql://{self._username}:{self._password}@{self._host}/{self._db_name}"

        self.engine: Engine = create_engine(self._connect_string)

        self.base.metadata.bind: Engine = self.engine

        # could not reuse session, implement session each needed
        self._session: sessionmaker = sessionmaker()
        self._session.configure(bind=self.engine)

        from . import models

    def get_session(self) -> Session:
        return self._session()

    def drop_all(self) -> None:
        self.base.metadata.drop_all()

    def create_all(self) -> None:
        self.base.metadata.create_all()

    def rebuild(self) -> None:
        self.drop_all()
        self.create_all()
