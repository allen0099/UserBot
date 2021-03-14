import logging

from sqlalchemy import BigInteger, Boolean, Column, Integer, String

from database.mixin import BaseMixin, TimestampMixin
from main import db

log: logging.Logger = logging.getLogger(__name__)


class User(db.base, BaseMixin, TimestampMixin):
    uid = Column(BigInteger)
    deleted = Column(Boolean, nullable=True)
    bot = Column(Boolean, nullable=True)
    verified = Column(Boolean, nullable=True)
    restricted = Column(Boolean, nullable=True)
    scam = Column(Boolean, nullable=True)

    first_name = Column(String(65))
    last_name = Column(String(65))
    username = Column(String(33))
    phone = Column(String(100))
    about = Column(String(71))
    lang_code = Column(String(10))

    common_chats_count = Column(Integer)

    def __init__(
            self,
            uid: int,
            deleted: bool = None,
            bot: bool = None,
            verified: bool = None,
            restricted: bool = None,
            scam: bool = None,

            first_name: str = None,
            last_name: str = None,
            username: str = None,
            phone: str = None,
            lang_code: str = None,

            common_chats_count: int = None,
            about: str = None
    ):
        self.uid = uid
        self.deleted = deleted
        self.bot = bot
        self.verified = verified
        self.restricted = restricted
        self.scam = scam

        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.lang_code = lang_code

        self.common_chats_count = common_chats_count
        self.about = about
