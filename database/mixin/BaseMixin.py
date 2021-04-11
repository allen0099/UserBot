import logging

from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.declarative import declared_attr

log: logging.Logger = logging.getLogger(__name__)


class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower() + 's'

    id = Column(BigInteger, primary_key=True)
