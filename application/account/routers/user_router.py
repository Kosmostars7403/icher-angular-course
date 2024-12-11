import os
from typing import Annotated

from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException, Query
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.crud import update_user, delete_user, upload_image_in_db, get_all_users, get_user_by_id, \
    get_user, get_user_subscriptions, get_test_users, delete_user_image, get_subscribers as get_user_subscribers
from application.account.filters import UserFilter
from application.account.helpers import get_current_active_user
from application.account.models import User, IMAGE_DIR
from application.account.schemas.user_schemas import UserReadSchema, UserUpdateSchema, UserReadSchemaShort
from database.db import get_async_session

disable_installed_extensions_check()

router = APIRouter(
    tags=['account'],
    prefix='/account',
)

IMAGE_EXTENSIONS = [
    'bmp', 'gif', 'ico', 'ief', 'jpe', 'jpeg', 'jpg',
    'pbm', 'pgm', 'png', 'pnm', 'ppm', 'ras', 'rgb',
    'svg', 'tif', 'tiff', 'xbm', 'xpm', 'xwd'
]

@router.get('/test_accounts', response_model=list[UserReadSchemaShort], status_code=status.HTTP_200_OK)
async def get_test_accounts(session: AsyncSession = Depends(get_async_session)):
    return await get_test_users(session=session)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserReadSchema)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.patch('/me', response_model=UserReadSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_me(new_data: UserUpdateSchema, current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):
    new_data = new_data.model_dump(exclude_none=True)

    if current_user.username == "test_user_ws":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot update test user')

    await update_user(user=current_user, data=new_data, session=session)

    return await get_user(current_user.username)


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):

    if current_user.username == "test_user_ws":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot delete test user')

    await delete_user(user=current_user, session=session)

    return {'message': 'User deleted'}


@router.post('/upload_image', status_code=status.HTTP_202_ACCEPTED, response_model=UserReadSchema)
async def load_image(current_user: Annotated[User, Depends(get_current_active_user)], image: UploadFile = File(...),
                     session: AsyncSession = Depends(get_async_session)):

    image_content = await image.read()
    image_type = image.filename.split('.')[-1]

    if image_type.lower() not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Image type {image_type} is not supported')

    filename = f"{current_user.username}.{image_type}"

    avatar_url = os.path.join(IMAGE_DIR, filename)

    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    with open(avatar_url, 'wb') as f:
        f.write(image_content)

    await upload_image_in_db(user=current_user, avatar_url=avatar_url, session=session)

    return await get_user(current_user.username)


@router.delete('/delete_image', status_code=status.HTTP_202_ACCEPTED, response_model=UserReadSchema)
async def delete_my_image(current_user: Annotated[User, Depends(get_current_active_user)],
                          session: AsyncSession = Depends(get_async_session)):

    await delete_user_image(user=current_user, session=session)
    return await get_user(current_user.username)


@router.get('/accounts', status_code=status.HTTP_200_OK)
async def get_accounts(current_user: Annotated[User, Depends(get_current_active_user)],
                       stack: str = '',
                       first_name: str = Query(alias='firstName', default=''),
                       last_name: str = Query(alias='lastName', default=''),
                       user_filter: UserFilter = FilterDepends(UserFilter),
                       session: AsyncSession = Depends(get_async_session)) -> Page[UserReadSchemaShort]:
    return paginate(await get_all_users(user=current_user, session=session, user_filter=user_filter, stack=stack,
                                        first_name=first_name, last_name=last_name))


@router.get('/{account_id}', status_code=status.HTTP_200_OK)
async def get_account(account_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):

    if user := await get_user_by_id(user_id=account_id, session=session):

        result = UserReadSchema.model_validate(user).model_dump(by_alias=True)
        result['isSubscribed'] = True if account_id in current_user.subscriptions else False

        return result

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


@router.post('/subscribe/{account_id}', status_code=status.HTTP_202_ACCEPTED)
async def subscribe(account_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):

    if account_id not in current_user.subscriptions and account_id != current_user.id:
        current_user.subscriptions.append(account_id)

        await update_user(user=current_user, data={'subscriptions': current_user.subscriptions},
                          session=session)

        return {'message': f'You are now subscribed'}

    else:
        return {'message': f'You are already subscribed'}


@router.delete('/subscribe/{account_id}', status_code=status.HTTP_202_ACCEPTED)
async def unsubscribe(account_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    if account_id in current_user.subscriptions:
        current_user.subscriptions.remove(account_id)

        await update_user(user=current_user, data={'subscriptions': current_user.subscriptions},
                          session=session)

        return {'message': f'You are now unsubscribed'}

    else:
        return {'message': f'You are not subscribed'}


@router.get('/subscriptions/', status_code=status.HTTP_200_OK)
async def get_subscriptions(current_user: Annotated[User, Depends(get_current_active_user)],
                            stack: str = '',
                            first_name: str = Query(alias='firstName', default=''),
                            last_name: str = Query(alias='lastName', default=''),
                            user_filter: UserFilter = FilterDepends(UserFilter),
                            session: AsyncSession = Depends(get_async_session)) -> Page[UserReadSchemaShort]:
    return paginate(
        await get_user_subscriptions(user=current_user, session=session, user_filter=user_filter, stack=stack,
                                     first_name=first_name, last_name=last_name))


@router.get('/subscribers/', status_code=status.HTTP_200_OK)
async def get_subscribers(current_user: Annotated[User, Depends(get_current_active_user)],
                          stack: str = '',
                          first_last_name: str = Query(alias='firstLastName', default=''),
                          user_filter: UserFilter = FilterDepends(UserFilter),
                          session: AsyncSession = Depends(get_async_session)) -> Page[UserReadSchemaShort]:
    return paginate(await get_user_subscribers(user=current_user, session=session, user_filter=user_filter, stack=stack,
                                               first_last_name=first_last_name))
