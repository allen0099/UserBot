from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.declarative import declared_attr


class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower() + 's'

    id = Column(BigInteger, primary_key=True)
