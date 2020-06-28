from typing import List

from sqlalchemy import *

from models import Base, session


class WithoutPermission(Base):
    __tablename__: str = "ChatsWithoutPermission"

    id: int = Column(
        Integer,
        primary_key=True
    )
    cid: int = Column(
        Integer
    )

    def __init__(self, cid: int) -> None:
        self.cid = cid

    def __repr__(self) -> str:
        return f"Chat {self.cid}"

    @staticmethod
    def add(_id: int) -> bool:
        _check: WithoutPermission = session.query(WithoutPermission).filter_by(cid=_id).first()
        if _check is None:
            session.add(WithoutPermission(_id))
            session.commit()
            return True
        return False

    @staticmethod
    def is_saved(_id: int):
        _check: WithoutPermission = session.query(WithoutPermission).filter_by(cid=_id).first()
        if _check is None:
            return False
        return True

    @staticmethod
    def get() -> List[int]:
        chats: List[WithoutPermission] = session.query(WithoutPermission).all()
        return [c.cid for c in chats]

    @staticmethod
    def clear() -> bool:
        session.query(WithoutPermission).delete()
        session.commit()
        return True
