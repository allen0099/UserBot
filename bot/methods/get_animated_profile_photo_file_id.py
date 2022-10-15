from pyrogram import raw
from pyrogram.file_id import FileId, FileType, ThumbnailSource

import bot


class GetAnimatedProfilePhotoFileId:
    async def get_animated_profile_photo_file_id(
        self: "bot.Bot",
        full_user: raw.types.UserFull,
    ) -> str:
        return FileId(
            dc_id=full_user.profile_photo.dc_id,  # Required
            file_type=FileType.PHOTO,  # Required
            media_id=full_user.profile_photo.id,
            access_hash=full_user.profile_photo.access_hash,  # Required
            file_reference=full_user.profile_photo.file_reference,  # Required
            local_id=0,
            volume_id=0,
            thumbnail_file_type=FileType.VIDEO,
            thumbnail_source=ThumbnailSource.THUMBNAIL,
            thumbnail_size=full_user.profile_photo.video_sizes[0].type,  # Required
        ).encode()
