from sqlalchemy import BigInteger, Boolean, Column, DateTime, func

from database import db


class User(db.base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    is_white = Column(Boolean, default=False)
    is_black = Column(Boolean, default=False)

    updated_at = Column(DateTime, default=func.now())

    def __init__(self, user_id: int, is_white: bool = False, is_black: bool = False):
        self.user_id = user_id
        self.is_white = is_white
        self.is_black = is_black

    def __str__(self):
        return f"{self.user_id}, {self.is_white}, {self.is_black}"

    @staticmethod
    def get_whitelist() -> list[int]:
        users: list["User"] = db.session.query(User) \
            .filter_by(is_white=True) \
            .all()

        return [_.user_id for _ in users]

    @staticmethod
    def get_blacklist() -> list[int]:
        users: list["User"] = db.session.query(User) \
            .filter_by(is_black=True) \
            .all()

        return [_.user_id for _ in users]

    @staticmethod
    def get_or_create(user_id: int) -> "User":
        _test = db.session.query(User).get(user_id)

        if _test:
            return _test

        user = User(user_id)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()
        return db.session.query(User).get(user_id)

    def set_null(self) -> None:
        self.is_white = False
        self.is_black = False
        db.session.add(self)
        db.session.commit()

    def set_white(self) -> None:
        self.is_white = True
        self.is_black = False
        db.session.add(self)
        db.session.commit()

    def set_black(self) -> None:
        self.is_white = False
        self.is_black = True
        db.session.add(self)
        db.session.commit()
