from sqlalchemy import BigInteger, Boolean, Column, DateTime, func

from database import db


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
