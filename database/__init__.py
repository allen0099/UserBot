import logging
import os
# noinspection PyProtectedMember
from typing import Union

from sqlalchemy import MetaData
# noinspection PyProtectedMember
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, registry, sessionmaker

log: logging.Logger = logging.getLogger(__name__)


class Database:
    # registry should be a global shared object
    registry: registry = registry()

    _instance: Union[None, "Database"] = None

    def __init__(self):
        self._host: str = os.getenv("DB_HOST")
        self._db_name: str = os.getenv("DB_DATABASE")
        self._username: str = os.getenv("DB_USERNAME")
        self._password: str = os.getenv("DB_PASSWORD")
        self._connect_string: str = f"mysql+pymysql://{self._username}:{self._password}@{self._host}/{self._db_name}"

        self.engine: Engine = create_engine(self._connect_string, future=True)

        self.base: declarative_base = self.registry.generate_base()

        self.metadata: MetaData = self.registry.metadata
        self.metadata.bind = self.engine

        # could not reuse session, implement session each needed
        self._session: sessionmaker = sessionmaker(self.engine, future=True)

        from . import models

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session(self) -> Session:
        return self._session()

    def drop_all(self) -> None:
        self.metadata.drop_all()

    def create_all(self) -> None:
        self.metadata.create_all()

    def rebuild(self) -> None:
        self.drop_all()
        self.create_all()
