from typing import List

from models import session
from models.chats.ChatMixin import ChatMixin


class AdminChats(ChatMixin):
    __tablename__: str = "AdminChats"

    def __init__(self, chat_id: int) -> None:
        super().__init__(chat_id)

    @staticmethod
    def add(chat_id: int) -> bool:
        chat: AdminChats = session.query(AdminChats).filter_by(chat_id=chat_id).first()
        if chat is None:
            session.add(AdminChats(chat_id))
            session.commit()
            return True
        return False

    @staticmethod
    def is_exist(chat_id: int) -> bool:
        chat: AdminChats = session.query(AdminChats).filter_by(chat_id=chat_id).first()
        if chat is None:
            return False
        return True

    @staticmethod
    def list_all() -> List[int]:
        chats: List[AdminChats] = session.query(AdminChats).all()
        return [chat.chat_id for chat in chats]
