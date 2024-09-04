from application.personal_chat.models import PersonalChat


async def is_not_my_chat(chat: PersonalChat, user_id: int):
    if chat.user_first_id == user_id or chat.user_second_id == user_id:
        return False

    return True
