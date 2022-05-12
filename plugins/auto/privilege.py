import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message

from database import db
from database.privilege import Privilege

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.group, group=-1)
async def privilege(_: Client, msg: Message) -> None:
    """
    Log user privilege when new update income and database not exist.
    """
    if msg.chat.type == ChatType.SUPERGROUP:
        group_id: int = msg.chat.id
        group = db.session.query(Privilege).get(group_id)

        if not group:
            log.debug(f"{msg.chat.title} not found in database, adding...")
            group: Privilege = Privilege(group_id)

            try:
                me = await msg.chat.get_member("me")
                if me.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    group.can_delete_messages = me.privileges.can_delete_messages
                    group.can_manage_video_chats = me.privileges.can_manage_video_chats
                    group.can_restrict_members = me.privileges.can_restrict_members
                    group.can_promote_members = me.privileges.can_promote_members
                    group.can_change_info = me.privileges.can_change_info
                    group.can_invite_users = me.privileges.can_invite_users
                    group.can_pin_messages = me.privileges.can_pin_messages
                    group.is_anonymous = me.privileges.is_anonymous

            except UserNotParticipant:
                log.debug(f"{msg.chat.title} not joined the group, excluding...")

            db.session.add(group)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return
            finally:
                db.session.commit()
