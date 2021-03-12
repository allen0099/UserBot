import datetime
import logging
from typing import Optional, Union

from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.raw.base import InputPeer, InputUser, UserFull
from pyrogram.raw.types import InputPeerUser
from sqlalchemy.orm import Session

from database.models import User
from main import db

log: logging.Logger = logging.getLogger(__name__)


async def get_user_full(cli: Client, uid: Union[int, str]) -> User:
    session: Session = db.get_session()
    cache_user: Optional[User] = session.query(User).filter_by(uid=uid).first()

    if cache_user is None:
        log.debug(f"{uid} not cached")
        return await refresh_user(cli, uid)

    if datetime.datetime.utcnow() < cache_user.expired_at:
        log.debug(f"{uid} cached")
        return cache_user
    log.debug(f"{uid} expired at {cache_user.expired_at}, now is {datetime.datetime.utcnow()}")
    return await refresh_user(cli, uid)


async def refresh_user(cli: Client, uid: Union[int, str]) -> User:
    session: Session = db.get_session()
    peer: InputPeer = await cli.resolve_peer(uid)

    log.debug(f"Refreshing {uid}")

    if isinstance(peer, InputPeerUser) or isinstance(peer, InputUser):
        full_user: UserFull = await cli.send(functions.users.GetFullUser(id=peer))

        cache_user: User = session.query(User).filter_by(uid=full_user.user.id).first()

        if cache_user is None:
            cache_user: User = User(
                full_user.user.id,
                full_user.user.deleted,
                full_user.user.bot,
                full_user.user.verified,
                full_user.user.restricted,
                full_user.user.scam,
                full_user.user.first_name,
                full_user.user.last_name,
                full_user.user.username,
                full_user.user.phone,
                full_user.user.lang_code,
                full_user.common_chats_count,
                full_user.about
            )
            session.add(cache_user)
        else:
            cache_user.deleted = full_user.user.deleted
            cache_user.bot = full_user.user.bot
            cache_user.verified = full_user.user.verified
            cache_user.restricted = full_user.user.restricted
            cache_user.scam = full_user.user.scam
            cache_user.first_name = full_user.user.first_name
            cache_user.last_name = full_user.user.last_name
            cache_user.username = full_user.user.username
            cache_user.phone = full_user.user.phone
            cache_user.lang_code = full_user.user.lang_code
            cache_user.common_chats_count = full_user.common_chats_count
            cache_user.about = full_user.about

            cache_user.expired_at = datetime.datetime.utcnow() + datetime.timedelta(hours=6)

        session.commit()

        return cache_user
