import logging

from core.log import main_logger
from .custom_resolve_peer import CustomResolvePeer
from .delete_range_messages import DeleteRangeMessages
from .get_chat_admins import GetChatAdmins

log: logging.Logger = main_logger(__name__)


class CustomFunctions(
    CustomResolvePeer,
    DeleteRangeMessages,
    GetChatAdmins,
):
    pass
