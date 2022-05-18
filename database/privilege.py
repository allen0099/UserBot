import logging
from typing import Optional

from pyrogram import enums, errors, types
from sqlalchemy import BigInteger, Boolean, Column, DateTime, func

from database import db

log: logging.Logger = logging.getLogger(__name__)


class Privilege(db.base):
    __tablename__ = "privileges"

    group_id = Column(BigInteger, primary_key=True)
    can_delete_messages = Column(Boolean, default=False)
    can_manage_video_chats = Column(Boolean, default=False)
    can_restrict_members = Column(Boolean, default=False)
    can_promote_members = Column(Boolean, default=False)
    can_change_info = Column(Boolean, default=False)
    can_invite_users = Column(Boolean, default=False)
    can_pin_messages = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)

    updated_at = Column(DateTime, default=func.now())

    def __init__(self, group_id, can_delete_messages=False, can_manage_video_chats=False, can_restrict_members=False,
                 can_promote_members=False, can_change_info=False, can_invite_users=False, can_pin_messages=False,
                 is_anonymous=False):
        self.group_id = group_id
        self.can_delete_messages = can_delete_messages
        self.can_manage_video_chats = can_manage_video_chats
        self.can_restrict_members = can_restrict_members
        self.can_promote_members = can_promote_members
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_pin_messages = can_pin_messages
        self.is_anonymous = is_anonymous

    def __repr__(self):
        return f"<Privilege {self.group_id}>"

    def __str__(self):
        return f"Privilege {self.group_id}"

    @staticmethod
    def admin_groups() -> list[int]:
        groups: list[Privilege] = db.session.query(Privilege) \
            .filter_by(can_delete_messages=True, can_restrict_members=True) \
            .all()

        return [group.group_id for group in groups]

    @staticmethod
    def get(group_id: int) -> Optional["Privilege"]:
        return db.session.query(Privilege).get(group_id)

    @staticmethod
    async def create(msg: types.Message) -> "Privilege":
        group: Privilege = Privilege(msg.chat.id)

        try:
            me = await msg.chat.get_member("me")

            if me.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                group.can_delete_messages = me.privileges.can_delete_messages
                group.can_manage_video_chats = me.privileges.can_manage_video_chats
                group.can_restrict_members = me.privileges.can_restrict_members
                group.can_promote_members = me.privileges.can_promote_members
                group.can_change_info = me.privileges.can_change_info
                group.can_invite_users = me.privileges.can_invite_users
                group.can_pin_messages = me.privileges.can_pin_messages
                group.is_anonymous = me.privileges.is_anonymous

        except errors.UserNotParticipant:
            log.debug(f"{msg.chat.title} not joined the group, excluding...")

        db.session.add(group)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()

        return Privilege.get(msg.chat.id)

    async def update(self, msg: types.Message):
        try:
            me = await msg.chat.get_member("me")

            if me.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                self.can_delete_messages = me.privileges.can_delete_messages
                self.can_manage_video_chats = me.privileges.can_manage_video_chats
                self.can_restrict_members = me.privileges.can_restrict_members
                self.can_promote_members = me.privileges.can_promote_members
                self.can_change_info = me.privileges.can_change_info
                self.can_invite_users = me.privileges.can_invite_users
                self.can_pin_messages = me.privileges.can_pin_messages
                self.is_anonymous = me.privileges.is_anonymous
            else:
                self.can_delete_messages = False
                self.can_manage_video_chats = False
                self.can_restrict_members = False
                self.can_promote_members = False
                self.can_change_info = False
                self.can_invite_users = False
                self.can_pin_messages = False
                self.is_anonymous = False

        except errors.UserNotParticipant:
            log.debug(f"{msg.chat.title} not joined the group, should destroy...")

        db.session.add(self)
        db.session.commit()
