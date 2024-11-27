import os
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, insert, update, func, or_, delete
from sqlalchemy.dialects.postgresql.array import CONTAINS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.account.models import User
from application.comment.models import Comment
from application.community.models import Community, ImageType
from application.community.schemas import CommunityCreateSchema, CommunityUpdateSchema
from application.post.models import Post


async def get_community_by_id(community_id: int, user: User, session: AsyncSession) -> Community | None:
    community = await session.get(Community, community_id, options=[
        selectinload(Community.posts).options(
            selectinload(Post.comments).options(selectinload(Comment.author), selectinload(Comment.comments)),
            selectinload(Post.likes)),
        selectinload(Community.admin)])

    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    community.subscribers_amount = len([subscriber for subscriber in community.subscribers])
    community.is_joined = user.id == community.admin_id or user.id in community.subscribers

    return community


async def get_all_communities(name: str | None, themes: str | None, tags: str | None, user: User, session: AsyncSession):
    stmt = select(Community).options(
        selectinload(Community.posts).options(
            selectinload(Post.comments).options(selectinload(Comment.author), selectinload(Comment.comments)),
            selectinload(Post.likes)),
        selectinload(Community.admin)
    ).order_by(Community.name)

    if themes:
        themes = themes.upper().split(',')
        stmt = stmt.filter(CONTAINS(Community.themes, themes))

    if tags:
        tags = tags.capitalize().split(',')
        stmt = stmt.filter(CONTAINS(Community.tags, tags))

    if name:
        stmt = stmt.filter(or_(func.similarity(Community.name, name) > 0.3, Community.name.ilike(f'%{name}%')))

    communities = (await session.execute(stmt)).scalars().all()

    for community in communities:
        community.subscribers_amount = len([subscriber for subscriber in community.subscribers])

        if user.id == community.admin_id or user.id in community.subscribers:
            community.is_joined = True

    return communities

async def create_community(community: CommunityCreateSchema, user: User, session: AsyncSession):
    if community.tags:
        community.tags = [tag.capitalize() for tag in community.tags]

    data = community.model_dump(exclude_none=True)
    data['admin_id'] = user.id

    stmt = insert(Community).values(**data).returning(Community.id)

    community_id = await session.scalar(stmt)
    await session.commit()

    return await get_community_by_id(community_id, user, session)


async def update_community(community_id: int, community: CommunityUpdateSchema, session: AsyncSession):
    if community.tags:
        community.tags = [tag.capitalize() for tag in community.tags]
    stmt = update(Community).where(Community.id == community_id).values(**community.model_dump(exclude_none=True))
    await session.execute(stmt)
    await session.commit()

async def upd_subscribers(community_id: int, subscribers: List[int], session: AsyncSession):
    stmt = update(Community).where(Community.id == community_id).values(subscribers=subscribers)
    await session.execute(stmt)
    await session.commit()


async def delete_community(community_id: int, user: User, session: AsyncSession):
    community = await get_community_by_id(community_id, user, session)

    if community.avatar_url:
        if os.path.exists(community.avatar_url):
            os.remove(community.avatar_url)

    if community.banner_url:
        if os.path.exists(community.banner_url):
            os.remove(community.banner_url)

    stmt = delete(Post).filter(Post.community_id == community_id)
    await session.execute(stmt)

    await session.delete(community)
    await session.commit()


async def upload_community_image_in_db(community_id: int, image_url: str, img_type: ImageType, session: AsyncSession):
    match img_type:
        case ImageType.BANNER:
            stmt = update(Community).where(Community.id == community_id).values(banner_url=image_url)
        case ImageType.AVATAR:
            stmt = update(Community).where(Community.id == community_id).values(avatar_url=image_url)

    await session.execute(stmt)
    await session.commit()


async def delete_community_image_in_db(community: Community, img_type: ImageType, session: AsyncSession):
    match img_type:
        case ImageType.BANNER:
            stmt = update(Community).where(Community.id == community.id).values(banner_url=None)

            if community.banner_url is not None:
                if os.path.exists(community.banner_url):
                    os.remove(community.banner_url)

        case ImageType.AVATAR:
            stmt = update(Community).where(Community.id == community.id).values(avatar_url=None)

            if community.avatar_url is not None:
                if os.path.exists(community.avatar_url):
                    os.remove(community.avatar_url)

    await session.execute(stmt)
    await session.commit()


async def get_community_subscribers(community_id: int, session: AsyncSession):
    stmt = select(Community).filter(Community.id == community_id)
    community = (await session.execute(stmt)).scalar_one()

    stmt = select(User).filter(User.id.in_(community.subscribers))
    subscribers = (await session.execute(stmt)).scalars().all()

    return subscribers