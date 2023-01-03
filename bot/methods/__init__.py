from .custom_resolve_peer import CustomResolvePeer
from .delete_range_messages import DeleteRangeMessages
from .get_animated_profile_photo_file_id import GetAnimatedProfilePhotoFileId
from .get_chat_admins import GetChatAdmins
from .get_chat_member_from_message import GetChatMemberFromMessage
from .get_full_channel import GetFullChannel
from .get_sticker_set import GetStickerSet
from .kick_chat_member import KickChatMember
from .send_log_message import SendLogMessage
from .set_anti_spam import SetAntiSpam


class CustomMethods(
    CustomResolvePeer,
    DeleteRangeMessages,
    GetAnimatedProfilePhotoFileId,
    GetChatAdmins,
    GetChatMemberFromMessage,
    GetFullChannel,
    GetStickerSet,
    KickChatMember,
    SendLogMessage,
    SetAntiSpam,
):
    pass
