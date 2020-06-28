from typing import List

from sqlalchemy import *

from models import Base, session


class WithPermission(Base):
    __tablename__: str = "ChatsWithPermission"

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
        _check: WithPermission = session.query(WithPermission).filter_by(cid=_id).first()
        if _check is None:
            session.add(WithPermission(_id))
            session.commit()
            return True
        return False

    @staticmethod
    def is_saved(_id: int):
        _check: WithPermission = session.query(WithPermission).filter_by(cid=_id).first()
        if _check is None:
            return False
        return True

    @staticmethod
    def get() -> List[int]:
        chats: List[WithPermission] = session.query(WithPermission).all()
        return [c.cid for c in chats]

    @staticmethod
    def clear() -> bool:
        session.query(WithPermission).delete()
        session.commit()
        return True
