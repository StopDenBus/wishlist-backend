FROM python:3.13-alpine3.21

ARG POETRY_VERSION=2.1.3

RUN pip install "poetry==${POETRY_VERSION}"

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1001 app && \
    adduser --disabled-password --home /app --ingroup app --uid 1001 app

USER app

WORKDIR /app

COPY --exclude=Dockerfile --exclude=.git --exclude=.git --chown=app:app . /app/

RUN chmod u+x /app/entrypoint.sh

RUN poetry install --no-root

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]