from application.account.models import User
from application.community.models import Community
from fastapi import HTTPException, status


async def validate_community_admin(user: User, community: Community):

    if user.id == community.admin_id:
       return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"It's not your community",
    )
