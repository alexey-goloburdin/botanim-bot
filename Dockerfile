FROM python:3.11.1

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

RUN apt update && apt install -y curl sqlite3

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install

CMD ["poetry", "run", "python", "-m", "botanim_bot"]
