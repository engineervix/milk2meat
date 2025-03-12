# Milk to Meat

> A simple tool to facilitate personal Bible Study

[![Continuous Integration](https://github.com/engineervix/milk2meat/actions/workflows/main.yml/badge.svg)](https://github.com/engineervix/milk2meat/actions/workflows/main.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/engineervix/d435cc3f4234a469e5df13bf019a6385/raw/covbadge.json)](https://github.com/engineervix/milk2meat/actions?query=workflow%3A%22%22Continuous+Integration%22%22++)

[![python3](https://img.shields.io/badge/python-3.13-brightgreen.svg)](https://python.org/)
[![Node v22](https://img.shields.io/badge/Node-v22-teal.svg)](https://nodejs.org/en/blog/release/v22.0.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code%20style-prettier-ff69b4.svg)](https://prettier.io/)

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![Conventional Changelog](https://img.shields.io/badge/changelog-conventional-brightgreen.svg)](https://github.com/conventional-changelog)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Development](#development)
- [Tips](#tips)
- [Credits](#credits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Development

This project requires

- [Postgres 15](https://www.postgresql.org/docs/15/index.html) (this is provided via [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) – see note below.)
- [Node.js 22](https://nodejs.org/en/blog/release/v22.14.0) on your system
- A [Python 3.13](https://docs.python.org/3/whatsnew/3.13.html) [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
- `libmagic` on your system ([homebrew](https://formulae.brew.sh/formula/libmagic) | [debian](https://packages.debian.org/stable/libmagic1) | [ubuntu](https://launchpad.net/ubuntu/noble/+package/libmagic1t64) | [fedora](https://packages.fedoraproject.org/pkgs/python-magic/python3-magic/))

> [!NOTE]
> When I started this project via `django-admin startproject milk2meat .`, I wanted to get up and running quickly, so I didn't bother to do a proper Docker Compose development setup. However, I don't like using a system-wide Postgres installation, so I set up Postgres using [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/).
> The `docker-compose.yml` file therefore only contains a `db` service for Postgres. I only added the `Dockerfile` for production deployment. While it can also be used for development, additional setup is required, and I didn't get the chance to do that. If that's what you really want to do, you might wanna have a look at a sample configuration from a project generated via [`cookiecutter-wagtail-vix`](https://github.com/engineervix/cookiecutter-wagtail-vix/). If I have time, I'll update the setup to something similar.

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

3. create the required `.env` file

```sh
cp -v .env.example .env
```

4. apply database migrations

```sh
./manage.py migrate
```

5. create a superuser

```sh
./manage.py createsuperuser
```

6. add Bible Books data

```sh
./manage.py populate_bible_books
```

7. add some fake notes for testing

```sh
./manage.py create_demo_notes
```

8. run the dev server (runs [Django dev server](https://docs.djangoproject.com/en/5.1/ref/django-admin/#runserver) and [webpack](https://webpack.js.org/concepts/) simultaneously, courtesy of [honcho](https://github.com/nickstenning/honcho)).

```sh
inv start
```

You should be able to access the site at <http://127.0.0.1:8000>

## Tips

- Run tests via `pytest`
- Run `invoke -l` to see all available [Invoke](https://www.pyinvoke.org/) tasks. These are defined in the [tasks.py](tasks.py) file.
- You'll want to setup [pre-commit](https://pre-commit.com/) by running `pre-commit install` followed by `pre-commit install --hook-type commit-msg`. Optionally run `pre-commit run --all-files` to make sure your pre-commit setup is okay.

## Credits

Illustrations

- <https://undraw.co>
- <https://www.svgrepo.com/svg/125463/open-book>
