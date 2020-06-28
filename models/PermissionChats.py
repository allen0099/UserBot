from typing import List

from sqlalchemy import *

from models import Base, session


class PermissionChats(Base):
    __tablename__: str = "PermissionChats"

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
        _check: PermissionChats = session.query(PermissionChats).filter_by(cid=_id).first()
        if _check is None:
            session.add(PermissionChats(_id))
            session.commit()
            return True
        return False

    @staticmethod
    def is_saved(_id: int):
        _check: PermissionChats = session.query(PermissionChats).filter_by(cid=_id).first()
        if _check is None:
            return False
        return True

    @staticmethod
    def get() -> List[int]:
        chats: List[PermissionChats] = session.query(PermissionChats).all()
        return [c.cid for c in chats]

    @staticmethod
    def clear() -> bool:
        session.query(PermissionChats).delete()
        session.commit()
        return True
