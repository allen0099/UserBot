import html
import logging
from datetime import datetime

from .resolve_peer import resolve_peer
from ..types import EMOJI

log: logging.Logger = logging.getLogger(__name__)


def get_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def get_mention_name(uid: int, first_name: str, last_name: str = None) -> str:
    return f"<a href='tg://user?id={uid}'>" \
           f"{html.escape(first_name) if first_name else EMOJI.empty}" \
           f"{' ' + html.escape(last_name) if last_name else EMOJI.empty}</a>"
