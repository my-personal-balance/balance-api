FROM python:3.12-alpine

ARG src=balance_api
ARG work_dir=/home/api

ARG YOUR_ENV=production

WORKDIR ${work_dir}

COPY ${src}/              ${work_dir}/${src}
COPY alembic/             ${work_dir}/alembic
COPY alembic.ini          ${work_dir}/
COPY uwsgi.ini            ${work_dir}/
COPY poetry.lock          ${work_dir}/
COPY pyproject.toml       ${work_dir}/
COPY README.md            ${work_dir}/

RUN apk add --no-cache g++ linux-headers libffi-dev
RUN pip install poetry

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --with=production --no-interaction --no-ansi

ENV PYTHONPATH=${work_dir}

CMD ["uwsgi", "--ini", "uwsgi.ini"]
