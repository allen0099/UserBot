from .custom_resolve_peer import CustomResolvePeer
from .delete_range_messages import DeleteRangeMessages
from .get_animated_profile_photo_file_id import GetAnimatedProfilePhotoFileId
from .get_chat_admins import GetChatAdmins
from .get_sticker_set import GetStickerSet
from .kick_chat_member import KickChatMember


class CustomMethods(
    CustomResolvePeer,
    DeleteRangeMessages,
    GetAnimatedProfilePhotoFileId,
    GetChatAdmins,
    GetStickerSet,
    KickChatMember,
):
    pass
