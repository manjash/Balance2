# FROM ghcr.io/br3ndonland/inboard:fastapi-0.37.0-python3.9
FROM ghcr.io/br3ndonland/inboard:fastapi-python3.11-slim

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* ./app/scripts/* /app/

WORKDIR /app/

# Allow installing dev dependencies to run tests
RUN pipx upgrade poetry
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-interaction --no-root -vvv; else poetry install --no-interaction --no-root --no-dev -vvv; fi"
RUN pip install --upgrade setuptools

# /start Project-specific dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# WORKDIR /app/
# /end Project-specific dependencies

ARG BACKEND_APP_MODULE=app.main:app
ARG BACKEND_PRE_START_PATH=/app/prestart.sh
ARG BACKEND_PROCESS_MANAGER=gunicorn
ARG BACKEND_WITH_RELOAD=false
ENV APP_MODULE=${BACKEND_APP_MODULE} PRE_START_PATH=${BACKEND_PRE_START_PATH} PROCESS_MANAGER=${BACKEND_PROCESS_MANAGER} WITH_RELOAD=${BACKEND_WITH_RELOAD}
COPY ./app/ /app/
