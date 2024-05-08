from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas, crud
from database.db import get_async_session
from typing import List

router = APIRouter(
    tags=['posts'],
    prefix='/posts',
)

@router.get("", response_model=List[schemas.Post])
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_posts(session=session)


@router.post("", response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, session: AsyncSession = Depends(get_async_session)):
    return await crud.create_post(session=session, title=post.title, content=post.content, author=post.author)


@router.get("/{post_id}", response_model=schemas.Post)
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    post = await crud.get_post(session=session, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

