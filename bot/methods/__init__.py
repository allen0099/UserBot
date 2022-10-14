from .custom_resolve_peer import CustomResolvePeer
from .delete_range_messages import DeleteRangeMessages
from .get_chat_admins import GetChatAdmins


class CustomMethods(
    CustomResolvePeer,
    DeleteRangeMessages,
    GetChatAdmins,
):
    pass
