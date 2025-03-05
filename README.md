# Milk to Meat

> A simple tool to facilitate personal Bible Study

## Development

This project requires

- Docker & Docker Compose, just for the Postgres Database
- Node.js 22 on your system
- A Python 3.13 virtual environment

Steps:

1. install dependencies

```sh
poetry install --with dev,docs,test --no-root
npm ci
```

2. fire up the postgres container

```sh
docker compose up -d --build  # First time
docker compose up -d          # Subsequent runs
```

Or you could use the [Invoke](https://www.pyinvoke.org/) commands:

```sh
inv up --build  # First time
inv up          # Subsequent runs
```

3. run the dev server (runs Django dev server and webpack simultaneously)

```sh
inv start
```

You should be able to access the site at <http://127.0.0.1:8000>
