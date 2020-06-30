from typing import List

from sqlalchemy import Column, Integer

from models import Base


class ChatMixin(Base):
    __abstract__ = True

    id: int = Column(
        Integer,
        primary_key=True
    )
    chat_id: int = Column(
        Integer
    )

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id

    def __repr__(self) -> str:
        return f"Chat {self.chat_id}"

    @staticmethod
    def add(chat_id: int) -> bool:
        return NotImplemented

    @staticmethod
    def is_exist(chat_id: int) -> bool:
        return NotImplemented

    @staticmethod
    def list_all() -> List[int]:
        return NotImplemented
