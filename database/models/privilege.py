import logging
from datetime import datetime
from typing import Optional

from pyrogram import enums, types
from sqlalchemy import BigInteger, Boolean, Column, DateTime, func
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class Privilege(db.BASE):
    __tablename__ = "privileges"

    group_id: int = Column(BigInteger, primary_key=True)
    """群組 ID"""

    can_manage_chat: bool = Column(Boolean, default=True)
    can_delete_messages: bool = Column(Boolean, default=False)
    can_manage_video_chats: bool = Column(Boolean, default=False)
    can_restrict_members: bool = Column(Boolean, default=False)
    can_promote_members: bool = Column(Boolean, default=False)
    can_change_info: bool = Column(Boolean, default=False)
    can_invite_users: bool = Column(Boolean, default=False)
    can_pin_messages: bool = Column(Boolean, default=False)
    is_anonymous: bool = Column(Boolean, default=False)

    created_at: datetime = Column(
        DateTime, nullable=False, default=func.now(), server_default=now()
    )
    updated_at: datetime = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=now(),
        onupdate=func.now(),
    )

    def __init__(
        self,
        group_id: int,
        *,
        can_manage_chat: bool = True,
        can_delete_messages: bool = False,
        can_manage_video_chats: bool = False,
        can_restrict_members: bool = False,
        can_promote_members: bool = False,
        can_change_info: bool = False,
        can_invite_users: bool = False,
        can_pin_messages: bool = False,
        is_anonymous: bool = False,
    ):
        self.group_id = group_id
        self.can_manage_chat: bool = can_manage_chat
        self.can_delete_messages: bool = can_delete_messages
        self.can_manage_video_chats: bool = can_manage_video_chats
        self.can_restrict_members: bool = can_restrict_members
        self.can_promote_members: bool = can_promote_members
        self.can_change_info: bool = can_change_info
        self.can_invite_users: bool = can_invite_users
        self.can_pin_messages: bool = can_pin_messages
        self.is_anonymous: bool = is_anonymous

    def __repr__(self):
        return f"<Privilege {self.group_id}>"

    def __str__(self):
        return f"Privilege {self.group_id}"

    @staticmethod
    def get(group_id: int) -> Optional["Privilege"]:
        return db.session.query(Privilege).get(group_id)

    @staticmethod
    def admin_group_list() -> list[int]:
        groups: list[Privilege] = (
            db.session.query(Privilege)
            .filter_by(can_delete_messages=True, can_restrict_members=True)
            .all()
        )

        return [group.group_id for group in groups]

    @staticmethod
    async def create_or_update(msg: types.Message) -> "Privilege":
        privileges: Privilege | None = Privilege.get(msg.chat.id)

        if not privileges:
            privileges: Privilege = Privilege(msg.chat.id)

        me: types.ChatMember = await msg.chat.get_member("me")

        if me.status in [
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        ]:
            privileges.can_manage_chat = me.privileges.can_manage_chat
            privileges.can_delete_messages = me.privileges.can_delete_messages
            privileges.can_manage_video_chats = me.privileges.can_manage_video_chats
            privileges.can_restrict_members = me.privileges.can_restrict_members
            privileges.can_promote_members = me.privileges.can_promote_members
            privileges.can_change_info = me.privileges.can_change_info
            privileges.can_invite_users = me.privileges.can_invite_users
            privileges.can_pin_messages = me.privileges.can_pin_messages
            privileges.is_anonymous = me.privileges.is_anonymous
        else:
            privileges.can_manage_chat = True
            privileges.can_delete_messages = False
            privileges.can_manage_video_chats = False
            privileges.can_restrict_members = False
            privileges.can_promote_members = False
            privileges.can_change_info = False
            privileges.can_invite_users = False
            privileges.can_pin_messages = False
            privileges.is_anonymous = False

        db.session.add(privileges)
        db.commit()

        return Privilege.get(msg.chat.id)
