from sqlalchemy import BigInteger, Column

from database import db


class Test(db.BASE):
    __tablename__ = "Test"

    user_id = Column(BigInteger, primary_key=True)
