from sqlalchemy import BigInteger, Column, DateTime, Integer, UniqueConstraint, func

from database import db


class GBanLog(db.base):
    __tablename__ = "gbanlogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    group_id = Column(BigInteger, nullable=False)

    updated_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='gban_unique'),
    )

    def __init__(self, user_id: int, group_id: int):
        self.user_id = user_id
        self.group_id = group_id

    @staticmethod
    def create(user_id: int, group_id: int) -> None:
        _data: GBanLog = GBanLog(user_id, group_id)
        db.session.add(_data)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def destroy(user_id: int) -> None:
        _data: list[GBanLog] = db.session.query(GBanLog) \
            .filter_by(user_id=user_id) \
            .all()
        for _ in _data:
            db.session.delete(_)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def get_banned_by_id(user_id: int) -> list[int]:
        _data: list[GBanLog] = db.session.query(GBanLog) \
            .filter_by(user_id=user_id) \
            .all()
        return [_.group_id for _ in _data]
