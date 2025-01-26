FROM python:3.12-slim
RUN pip install poetry==2.0.1
WORKDIR /app
COPY pyproject.toml ./ 
COPY poetry.lock ./
COPY src/ ./src/

RUN poetry lock
RUN poetry install --with datafetch

WORKDIR /app/src/data_fetch

ENTRYPOINT [ "poetry", "run", "python", "main.py" ]