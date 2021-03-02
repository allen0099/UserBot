from typing import List

from sqlalchemy import *

from _models_old import Base, session


class Users(Base):
    __tablename__: str = "Users"

    id: int = Column(
        Integer,
        primary_key=True
    )
    uid: int = Column(
        Integer
    )

    def __init__(self, uid: int) -> None:
        self.uid = uid

    def __repr__(self) -> str:
        return f"User {self.uid}"

    @staticmethod
    def add(uid: int) -> bool:
        user: Users = session.query(Users).filter_by(uid=uid).first()
        if user is None:
            session.add(Users(uid))
            session.commit()
            return True
        return False

    @staticmethod
    def remove(uid: int) -> bool:
        user: Users = session.query(Users).filter_by(uid=uid).first()
        if user is not None:
            session.delete(user)
            session.commit()
            return True
        return False

    @staticmethod
    def get() -> List[int]:
        users: List[Users] = session.query(Users).all()
        return [u.uid for u in users]
