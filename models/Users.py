from sqlalchemy import *

from models import Base


class Users(Base):
    __tablename__ = "Users"

    id = Column(
        Integer,
        primary_key=True
    )
    uid = Column(
        String
    )

    def __init__(self, uid):
        self.uid = uid

    def __repr__(self):
        return f"User {self.uid}"
