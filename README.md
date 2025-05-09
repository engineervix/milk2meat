# Milk to Meat

> A tool to facilitate personal Bible Study

[![Continuous Integration](https://github.com/engineervix/milk2meat/actions/workflows/main.yml/badge.svg)](https://github.com/engineervix/milk2meat/actions/workflows/main.yml)
[![Python Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/engineervix/d435cc3f4234a469e5df13bf019a6385/raw/covbadge.json)](https://github.com/engineervix/milk2meat/actions)
[![JS Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/engineervix/c2c521fe0d35ef3db3801b3203ed1fe4/raw/0e33fd7fde3c4fa95f7c6c99314a079a87cfec6c/covbadge.json)](https://github.com/engineervix/milk2meat/actions)

[![python3](https://img.shields.io/badge/python-3.13-brightgreen.svg)](https://python.org/)
[![Node v22](https://img.shields.io/badge/Node-v22-teal.svg)](https://nodejs.org/en/blog/release/v22.0.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code%20style-prettier-ff69b4.svg)](https://prettier.io/)

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![Conventional Changelog](https://img.shields.io/badge/changelog-conventional-brightgreen.svg)](https://github.com/conventional-changelog)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [About](#about)
- [Features](#features)
- [Development](#development)
- [Deployment](#deployment)
  - [Docker Compose Deployment](#docker-compose-deployment)
- [Tips](#tips)
- [Credits](#credits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## About

![screenshot](https://github.com/user-attachments/assets/d53e9f63-ad1b-4f10-bf54-bf8812e3eaa3)

Milk2Meat is a personal Bible study tool inspired by [Hebrews 5:13-14](https://biblia.com/bible/esv/hebrews/5/13-14) and [1 Corinthians 3:1-2](https://biblia.com/bible/esv/1-corinthians/3/1-2), representing the journey from spiritual milk (basics) to meat (deeper understanding). I wrote it with a view to engage more deeply with the Scriptures through structured note-taking, book introductions, and organized Bible study.

The name reflects the spiritual growth process:

> "For everyone who lives on milk is unskilled in the word of righteousness, since he is a child. But solid food is for the mature, for those who have their powers of discernment trained by constant practice to distinguish good from evil." - Hebrews 5:13-14

## Features

- **Book Introductions**: Add detailed introductions to each book of the Bible (inspired by [The Reformation Study Bible](https://www.reformationstudybible.com/) and [The ESV Global Study Bible](https://www.crossway.org/bibles/esv-global-study-bible-hconly/))
- **Note Taking**: Create and organize study notes, sermon notes, and devotionals
- **File Attachments**: Upload handwritten notes or other files (PDFs, images)
- **References**: Link notes to specific Bible books
- **Tags**: Organize notes with custom tagging
- **Markdown Support**: Rich text editing with Markdown (powered by [EasyMDE](https://github.com/Ionaru/easy-markdown-editor))
- **Search**: Full-text search across all your content
- **Private**: All notes and attached files are private to your user account
- **Dark Mode**: Support for light and dark themes

## Development

This project requires

- [Postgres 15](https://www.postgresql.org/docs/15/index.html) (this is provided via [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) – see note below.)
- [Node.js 22](https://nodejs.org/en/blog/release/v22.14.0) on your system
- A [Python 3.13](https://docs.python.org/3/whatsnew/3.13.html) [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
- `libmagic` on your system ([homebrew](https://formulae.brew.sh/formula/libmagic) | [debian](https://packages.debian.org/stable/libmagic1) | [ubuntu](https://launchpad.net/ubuntu/noble/+package/libmagic1t64) | [fedora](https://packages.fedoraproject.org/pkgs/python-magic/python3-magic/))

> [!NOTE]
> When I started this project via `django-admin startproject milk2meat .`, I wanted to get up and running quickly, so I didn't bother to do a proper Docker Compose development setup. However, I don't like using a system-wide Postgres installation, so I set up Postgres using [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/).
>
> The development docker compose config file is located in `docker/docker-compose.dev.yml` and only contains a `db` service for Postgres.
>
> For production, there's a separate `docker-compose.yml` in the root directory that contains the complete stack.

Steps:

1. install dependencies

```sh
poetry install --with dev,docs,test --no-root
npm ci
```

2. configure environment variables

```sh
cp -v .dev.env.example .dev.env
```

3. fire up the postgres container

```sh
inv up --build  # First time
inv up          # Subsequent runs
```

> [!NOTE]
> You don't need `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` during development.

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

## Deployment

> [!IMPORTANT]
> This application is configured to use [Cloudflare R2](https://developers.cloudflare.com/r2/) for media storage, and [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/), a verification tool to replace CAPTCHAs. You'll need to set those up and provide the necessary environment variables.

### Docker Compose Deployment

The [`docker-compose.yml`](./docker-compose.yml) is configured to work with [Traefik](https://traefik.io/), based on the following requirements:

- A server with Docker and Docker Compose installed
- [Traefik](https://traefik.io/) already set up and configured [like this](https://gitlab.com/engineervix/run-core-traefik)
- Domain name pointing to your server

1. Copy the example environment file to `.env` and edit the latter with your production settings:

   ```sh
   cp .env.example .env
   ```

2. Spin up the containers and start the application:

   ```sh
   docker compose up -d --build
   ```

3. Create a superuser:

   ```sh
   docker compose exec milk2meat python manage.py createsuperuser
   ```

4. Populate Bible books data:
   ```sh
   docker compose exec milk2meat python manage.py populate_bible_books
   ```

That's it! The application should be running at your configured domain with Traefik handling SSL certificates.

### Dokku Deployment

You'd have to remove the following lines from the Dockerfile:

```Dockerfile
# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
```

I wrote [`bin/deploy.sh`](./bin/deploy.sh) for deployment to a machine running [Dokku](https://dokku.com/). It's accompanied by [`bin/.deploy.env.example`](./bin/.deploy.env.example) which shows the required environment variables.

## Tips

- Run python tests via `pytest`
- Run javascript tests via `npm test`
- Run `invoke -l` to see all available [Invoke](https://www.pyinvoke.org/) tasks. These are defined in the [tasks.py](tasks.py) file.
- You'll want to setup [pre-commit](https://pre-commit.com/) by running `pre-commit install` followed by `pre-commit install --hook-type commit-msg`. Optionally run `pre-commit run --all-files` to make sure your pre-commit setup is okay.

## Credits

Illustrations

- <https://undraw.co>
- <https://www.svgrepo.com/svg/125463/open-book>
