import pyrogram


def have_permission(member: pyrogram.ChatMember) -> bool:
    if member.status == "creator" or \
            member.status == "administrator" and \
            member.can_delete_messages is True and \
            member.can_restrict_members is True:
        return True
    return False
