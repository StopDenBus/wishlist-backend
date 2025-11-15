FROM python:3.14-alpine3.22

ARG POETRY_VERSION=2.1.3

RUN pip install "poetry==${POETRY_VERSION}"

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

RUN apk add cargo

# Create a custom user with UID 1234 and GID 1234
RUN addgroup --gid 1001 app && \
    adduser --disabled-password --home /app --ingroup app --uid 1001 app

USER app

WORKDIR /app

COPY --chown=app:app . /app/

RUN chmod u+x /app/entrypoint.sh

RUN poetry lock && poetry install --no-root

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]