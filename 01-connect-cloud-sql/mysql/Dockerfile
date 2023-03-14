### Base
FROM python:3.11.1-alpine as base

# Set environment variables used in builder and final images
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv

WORKDIR /app


### Builder
FROM base as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.3.2 \
    PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv $VIRTUAL_ENV

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | $VIRTUAL_ENV/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && $VIRTUAL_ENV/bin/pip install dist/*.whl


### Production
FROM base as production
COPY --from=builder /venv /venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Set default port number as same as the one for Cloud Run
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
