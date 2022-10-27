FROM python:alpine

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
COPY .ssh                 ${work_dir}/.ssh

RUN apk add --no-cache g++ linux-headers
RUN pip install poetry

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" = production && echo "--with=production") --no-interaction --no-ansi

ENV PYTHONPATH=${work_dir}

CMD ["uwsgi", "--ini", "uwsgi.ini"]
