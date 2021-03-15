import logging

from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from database.mixin import BaseMixin
from main import db

log: logging.Logger = logging.getLogger(__name__)


class ChatBannedRights(db.base, BaseMixin):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    until_date = Column(Integer, nullable=False)
    send_messages = Column(Boolean, nullable=False)
    send_media = Column(Boolean, nullable=False)
    send_stickers = Column(Boolean, nullable=False)
    send_gifs = Column(Boolean, nullable=False)
    send_games = Column(Boolean, nullable=False)
    send_inline = Column(Boolean, nullable=False)
    embed_links = Column(Boolean, nullable=False)
    send_polls = Column(Boolean, nullable=False)
    change_info = Column(Boolean, nullable=False)
    invite_users = Column(Boolean, nullable=False)
    pin_messages = Column(Boolean, nullable=False)

    channel = relationship("Channel", back_populates="default_banned_rights")
