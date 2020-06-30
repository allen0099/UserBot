from typing import List

from models import session
from models.chats.ChatMixin import ChatMixin


class MemberChats(ChatMixin):
    __tablename__: str = "MemberChats"

    def __init__(self, chat_id: int) -> None:
        super().__init__(chat_id)

    @staticmethod
    def add(chat_id: int) -> bool:
        chat: MemberChats = session.query(MemberChats).filter_by(chat_id=chat_id).first()
        if chat is None:
            session.add(MemberChats(chat_id))
            session.commit()
            return True
        return False

    @staticmethod
    def is_exist(chat_id: int) -> bool:
        chat: MemberChats = session.query(MemberChats).filter_by(chat_id=chat_id).first()
        if chat is None:
            return False
        return True

    @staticmethod
    def list_all() -> List[int]:
        chats: List[MemberChats] = session.query(MemberChats).all()
        return [chat.chat_id for chat in chats]
