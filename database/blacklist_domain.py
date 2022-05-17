from sqlalchemy import Column, DateTime, String, func

from database import db


class BlackListDomain(db.base):
    __tablename__ = "blacklist_domains"

    name = Column(String(100), primary_key=True)

    updated_at = Column(DateTime, default=func.now())

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def add(domain: str) -> None:
        _data: BlackListDomain = BlackListDomain(domain)
        db.session.add(_data)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def destroy(name: str) -> None:
        _data: list[BlackListDomain] = db.session.query(BlackListDomain) \
            .filter_by(name=name) \
            .first()

        for _ in _data:
            db.session.delete(_)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def get_list() -> list[str]:
        domains: list["BlackListDomain"] = db.session.query(BlackListDomain) \
            .all()

        return [_.name for _ in domains]
