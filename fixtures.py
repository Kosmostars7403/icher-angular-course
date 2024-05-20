import asyncio
from application.account.random_generator import password_generator
from application.account.validation import get_password_hash
from database.db import async_session
from application.account.models import User
from application.post.models import Post  # Не удалять
from application.comment.models import Comment  # Не удалять
from sqlalchemy import select


async def create_user(id: int,
                      first_name: str,
                      last_name: str,
                      username: str,
                      avatar_url: str,
                      stack: list[str],
                      city: str,
                      description: str,
                      subscriptions: list[int]
                      ) -> None:
    async with async_session() as session:
        user = {
            'id': id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'avatar_url': avatar_url,
            'stack': stack,
            'city': city,
            'description': description,
            'subscriptions': subscriptions
        }

        password = await password_generator()
        user['hashed_password'] = get_password_hash(password)

        user = User(**user)
        session.add(user)
        await session.commit()


async def main():
    async with async_session() as session:
        stmt = select(User).where(User.id == 123)
        result = await session.execute(stmt)

        if result.scalar() is None:
            await create_user(
                id=123,
                first_name='Дмитрий',
                last_name='Шевченко',
                username='dimonshev',
                avatar_url='static/avatars/dimonshev.jpg',
                stack=['Python', 'Django', 'FastAPI', 'React', 'SQLAlchemy', 'PostgreSQL', 'Alembic', 'Docker'],
                city='Москва',
                description='Я python-backend разработчик из Москвы, люблю писать код и помогать другим!',
                subscriptions=[]
            )
            await create_user(
                id=124,
                first_name='Миша',
                last_name='Сергеев',
                username='michael123',
                avatar_url='static/avatars/michael123.jpg',
                stack=['JavaScript', 'Node.js', 'Express.js', 'React', 'MongoDB', 'GraphQL', 'Apollo Server', 'Docker'],
                city='Saratov',
                description='Я JS разработчик из Санкт-Петербурга, всегда на связи!',
                subscriptions=[123]
            )

            await create_user(
                id=125,
                first_name='Анна',
                last_name='Самойлова',
                username='annsam',
                avatar_url='static/avatars/annsam.jpg',
                stack=['Pytest', 'autotest', 'unittest', 'Python'],
                city='Moscow',
                description='Я тестировщик, которого не боятся :)',
                subscriptions=[123, 124]
            )

            await create_user(
                id=126,
                first_name='Алексей',
                last_name='Смирнов',
                username='alexsmirn',
                avatar_url='static/avatars/alexsmirn.jpg',
                stack=['TypeScript', 'Node.js', 'Angular'],
                city='Екатеринбург',
                description='Я Angular разработчик, спец по сайтам и фрилансу!',
                subscriptions=[123, 124, 125]
            )
            await create_user(
                id=127,
                first_name='Татьяна',
                last_name='Конькова',
                username='tatsiko',
                avatar_url='static/avatars/tatsiko.jpg',
                stack=['C++', 'Qt', 'Linux', 'CMake', 'PostgreSQL', 'C#', 'Docker'],
                city='Москва',
                description='Я C++ разработчик, прошел три круга ада и знаю все, что нужно!',
                subscriptions=[123, 124, 125, 126]
            )


if __name__ == '__main__':
    asyncio.run(main())
