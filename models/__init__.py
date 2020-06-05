from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker

# https://stackoverflow.com/a/45613994

engine: Engine = create_engine("sqlite:///:memory:", echo=True)

Base: DeclarativeMeta = declarative_base()

DBSession: sessionmaker = sessionmaker(bind=engine)
session: sessionmaker = DBSession()

from .Users import Users
