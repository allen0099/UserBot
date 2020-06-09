from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session

# https://stackoverflow.com/a/45613994

engine: Engine = create_engine("sqlite:///settings.db", echo=True,
                               connect_args=dict(check_same_thread=False))

Base: DeclarativeMeta = declarative_base()

_session: sessionmaker = sessionmaker(bind=engine)
session: Session = _session()

from .Users import Users
