# Icher Angular Course

Backend сервиса для курса по Angular. Проект построен на FastAPI, PostgreSQL, Redis и SQLAlchemy; миграции базы данных управляются Alembic.

## Для AI-агентов

- Перед изменениями изучите соответствующие модули в `application/`, настройки в `settings.py` и схему базы в `database/`.
- Не добавляйте реальные пароли, токены и ключи в код, README или историю Git. Локальные переменные храните в `.env`; этот файл исключён через `.gitignore`.
- Изменения схемы базы оформляйте миграциями Alembic в `migrations/`.
- Для локального запуска используйте Docker Compose: backend, PostgreSQL и Redis должны работать вместе.
- При изменении запуска, зависимостей или переменных окружения обновляйте этот README.

## Локальный запуск

Требования: Git, Docker Engine и Docker Compose plugin.

1. Клонируйте репозиторий и перейдите в него:

   ```bash
   git clone https://github.com/Kosmostars7403/icher-angular-course.git
   cd icher-angular-course
   ```

2. Создайте в корне файл `.env` и скопируйте в него шаблон ниже. Значения ключей здесь предназначены только для локальной разработки; для любого публичного или постоянного окружения задайте собственные секреты.

   ```dotenv
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=angular_course
   ROOT_URL=/yt-course

   ACCESS_TOKEN_EXPIRE_MINUTES=5
   REFRESH_TOKEN_EXPIRE_DAYS=30
   SECRET_KEY_JWT=local-development-jwt-key
   SECRET_KEY_AUTH=local-development-auth-key
   LIMIT_SEC=60
   LIMIT_TIMES=10
   ```

3. Запустите сервисы:

   ```bash
   make run
   ```

   Команда создаст каталог `static/`, соберёт образы и запустит контейнеры в фоне. При первом запуске backend применит миграции и загрузит тестовые данные.

4. Откройте документацию API: [http://localhost:8000/yt-course/docs](http://localhost:8000/yt-course/docs). Альтернативная документация: [http://localhost:8000/yt-course/redoc](http://localhost:8000/yt-course/redoc).

Остановка контейнеров:

```bash
make stop
```

Данные PostgreSQL и Redis сохраняются в Docker volumes между остановками. Чтобы посмотреть логи:

```bash
docker compose logs -f backend
```
