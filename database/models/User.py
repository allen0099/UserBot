import datetime

from sqlalchemy import BigInteger, Column, Integer, String, TIMESTAMP

from bot import Bot


class User(Bot.base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)

    uid = Column(BigInteger)
    first_name = Column(String(65))
    last_name = Column(String(65))
    username = Column(String(33))
    about = Column(String(71))

    common_chats_count = Column(Integer)

    expires_at = Column(TIMESTAMP,
                        default=datetime.datetime.utcnow() + datetime.timedelta(hours=6))
