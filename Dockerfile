FROM python:3.11

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONBUFFERED 1

RUN pip install poetry


COPY poetry.lock pyproject.toml /backend/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

RUN mkdir -p static

RUN cp -r images/* static

EXPOSE 8000