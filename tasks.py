import datetime
import os
from pathlib import Path

import tomli
from colorama import Fore, init
from invoke import task


@task
def dev(c):
    """run the Django development server"""
    c.run("python manage.py runserver 0.0.0.0:8000", pty=True)


@task
def start(c):
    """Run this to fire up the django server & frontend tools"""
    # https://github.com/nickstenning/honcho
    c.run("honcho -f docker/Procfile start", pty=True)


@task
def test(c):
    """run tests"""
    c.run("pytest", pty=True)


@task
def db_snapshot(c, filename_prefix):
    """Create a Database snapshot using DSLR"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    (
        c.run(
            "dslr snapshot {filename_prefix}_{timestamp}".format(
                filename_prefix=filename_prefix,
                timestamp=timestamp,
            ),
            pty=True,
        ),
    )


@task(help={"build": "Build images before starting containers."})
def up(c, build=False):
    """docker-compose up -d"""
    if build:
        c.run(
            "docker-compose up -d --build",
            pty=True,
        )
    else:
        c.run("docker-compose up -d", pty=True)


@task
def exec(c, container, command):
    """docker-compose exec [container] [command(s)]"""
    c.run(f"docker-compose exec {container} {command}", pty=True)


@task(help={"follow": "Follow log output"})
def logs(c, container, follow=False):
    """docker-compose logs [container] [-f]"""
    if follow:
        c.run(f"docker-compose logs {container} -f", pty=True)
    else:
        c.run(f"docker-compose logs {container}", pty=True)


@task
def stop(c):
    """docker-compose stop"""
    c.run("docker-compose stop", pty=True)


@task(
    help={
        "volumes": "Remove named volumes declared in the `volumes` section of the Compose file and anonymous volumes attached to containers."
    }
)
def down(c, volumes=False):
    """docker-compose down"""
    if volumes:
        c.run("docker-compose down -v", pty=True)
    else:
        c.run("docker-compose down", pty=True)


@task(help={"dump_file": "The name of the dump file to import"})
def restore_db(c, dump_file):
    """
    Import a database dump into the database container

    1. Copy the dump file into the db container
    2. drop existing database
    3. create new database
    4. import dump file into database
    5. clean up
    """
    # Extract filename from the dump_file path
    dump_filename = os.path.basename(dump_file)
    db_password = "milk2meat"

    # copy dump file into db container
    c.run(f"docker cp {dump_file} milk2meat-db-1:/tmp/{dump_filename}", pty=True)

    # drop existing database with password
    c.run(
        f'inv exec "db" "/bin/bash -c \'PGPASSWORD={db_password} dropdb --if-exists --host db --username=milk2meat milk2meat\'"',
        pty=True,
    )

    # create new database with password
    c.run(
        f'inv exec "db" "/bin/bash -c \'PGPASSWORD={db_password} createdb --host db --username=milk2meat milk2meat\'"',
        pty=True,
    )

    # import dump file into database with password
    c.run(
        f'inv exec "db" "/bin/bash -c \'PGPASSWORD={db_password} pg_restore --clean --no-acl --if-exists --no-owner --host db --username=milk2meat -d milk2meat /tmp/{dump_filename}\'"',
        pty=True,
    )

    # clean up
    c.run(f'inv exec "db" "rm -vf /tmp/{dump_filename}"', pty=True)


@task
def backup_db(c):
    """
    Create a database backup and save it locally in ./.backups directory

    1. Ensure .backups directory exists
    2. Generate a timestamped filename
    3. Create database dump
    4. Copy the dump from container to local .backups directory
    5. Clean up dump file in container
    """
    # Ensure .backups directory exists
    backup_dir = "./.backups"
    if not os.path.exists(backup_dir):
        c.run(f"mkdir -p {backup_dir}", pty=True)

    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_filename = f"milk2meat_backup_{timestamp}.dump"
    container_path = f"/tmp/{dump_filename}"

    # Create database dump in container with password
    db_password = "milk2meat"
    c.run(
        f'inv exec "db" "/bin/bash -c \'PGPASSWORD={db_password} pg_dump -Fc --no-acl --no-owner --host db --username=milk2meat milk2meat > {container_path}\'"',
        pty=True,
    )

    # Copy dump from container to local machine
    local_path = os.path.join(backup_dir, dump_filename)
    c.run(f"docker cp milk2meat-db-1:{container_path} {local_path}", pty=True)

    # Clean up dump file in container
    c.run(f'inv exec "db" "rm -vf {container_path}"', pty=True)

    print(f"Backup saved to {local_path}")
    return local_path


@task(help={"fix": "let black and ruff format your files"})
def lint(c, fix=False):
    """ruff and black"""

    if fix:
        c.run("black .", pty=True)
        c.run("ruff check --fix .", pty=True)
    else:
        c.run("black . --check", pty=True)
        c.run("ruff check .", pty=True)


@task
def clean_pyc(c):
    """remove Python file artifacts"""

    c.run("find . -name '*.pyc' -exec rm -f {} +", pty=True)
    c.run("find . -name '*.pyo' -exec rm -f {} +", pty=True)
    c.run("find . -name '__pycache__' -exec rm -fr {} +", pty=True)
    c.run('find . -type d -name "*.egg-info" -exec rm -fr {} +', pty=True)
    c.run('find . -type d -name ".ruff_cache" -exec rm -fr {} +', pty=True)


@task
def clean_test(c):
    """remove test and coverage artifacts"""

    c.run("rm -fr .tox/", pty=True)
    c.run("rm -f .coverage", pty=True)
    c.run("rm -f coverage.xml", pty=True)
    c.run("rm -f coverage.json", pty=True)
    c.run("rm -fr htmlcov/", pty=True)
    c.run("rm -fr .pytest_cache", pty=True)


@task
def clean(c):
    """remove both Python file and test artifacts"""

    clean_pyc(c)
    clean_test(c)


def create_release(c, branch, is_first_release=False, push=False):
    """Create a release by combining `commitizen-tools` and `commit-and-tag-version`

    commitizen-tools works best with Python projects, but I don't like the
    generated changelogs. I had no time to look at how to customize them, so I
    decided to use commit-and-tag-version (which works best with Node.js projects).
    Unfortunately, commit-and-tag-version by default doesn't work with Python projects,
    and since I didn't have time to write my own updater for python files and toml files,
    I have to make the two work together!

    This requires commit-and-tag-version to be installed in your project:
    ``npm i -D commit-and-tag-version``

    The logic is as follows:

    1. cz bump --files-only
    2. git add pyproject.toml and other_files specified in pyproject.toml
    3. commit-and-tag-version --commit-all --release-as <result from cz if not none>
    4. git push --follow-tags origin [branch]
    """
    if is_first_release:  # tag a release without bumping the version bumpFiles
        with open("pyproject.toml", "rb") as f:
            toml_dict = tomli.load(f)
        project = toml_dict["tool"]["poetry"]["name"]
        print(f"{Fore.YELLOW}Generating your changelog for your first release ...{Fore.RESET}")
        c.run(
            f'npm run release -- --first-release --releaseCommitMessageFormat "chore: This is {project} v{{{{currentTag}}}} 🎉"',
            pty=True,
        )
        if push:
            # push to origin
            c.run(f"git push --follow-tags origin {branch}", pty=True)
    else:
        print(f"{Fore.MAGENTA}Attempting to bump using commitizen-tools ...{Fore.RESET}")
        c.run("cz bump --files-only > .bump_result.txt", pty=True)
        str_of_interest = "increment detected: "
        result = ""
        with open(".bump_result.txt", "r") as br:
            for line in br:
                if str_of_interest in line:
                    result = line
                    break
        release_type = result.replace(str_of_interest, "").strip("\n").lower()
        print(f"cz bump result: {release_type}")
        if release_type == "none":
            print(f"{Fore.YELLOW}No increment detected, cannot bump{Fore.RESET}")
        elif release_type in ["major", "minor", "patch"]:
            print(f"{Fore.GREEN}Looks like the bump command worked!{Fore.RESET}")
            print(f"{Fore.GREEN}Now handing over to commit-and-tag-version ...{Fore.RESET}")
            # first, stage the bumped files
            with open("pyproject.toml", "rb") as f:
                toml_dict = tomli.load(f)
            version_files = toml_dict["tool"]["commitizen"]["version_files"]
            files_to_add = " ".join(version_files)
            c.run(
                f"git add pyproject.toml {files_to_add}",
                pty=True,
            )
            # now we can pass result to standard-release
            print(f"{Fore.GREEN}let me retrieve the tag we're bumping from ...{Fore.RESET}")
            get_current_tag = c.run(
                "git describe --abbrev=0 --tags `git rev-list --tags --skip=0  --max-count=1`",
                pty=True,
            )
            previous_tag = get_current_tag.stdout.rstrip()

            c.run(
                f'npm run release -- --commit-all --release-as {release_type} --releaseCommitMessageFormat "bump: ✈️ {previous_tag} → v{{{{currentTag}}}}"',
                pty=True,
            )
            if push:
                # push to origin
                c.run(f"git push --follow-tags origin {branch}", pty=True)
        else:
            print(f"{Fore.RED}Something went horribly wrong, please investigate & fix it!{Fore.RESET}")
            print(f"{Fore.RED}Bump failed!{Fore.RESET}")

        # clean up
        c.run("rm -vf .bump_result.txt", pty=True)


@task(
    help={
        "branch": "The branch against which you wanna bump",
        "first": "Is this the first release?",
    }
)
def bump(c, branch, first=False):
    """Use Commitizen Tools & commit-and-tag-version to bump version and generate changelog

    Run this task when you want to prepare a release.
    First we check that there are no unstaged files before running
    """

    init()

    unstaged_str = "not staged for commit"
    uncommitted_str = "to be committed"
    check = c.run("git status", pty=True)
    if unstaged_str not in check.stdout or uncommitted_str not in check.stdout:
        create_release(c, branch, first, push=False)
    else:
        print(f"{Fore.RED}Sorry mate, please ensure there are no unstaged files before creating a release{Fore.RESET}")


@task
def get_release_notes(c):
    """extract content from CHANGELOG.md for use in Github/Gitlab Releases

    we read the file and loop through line by line
    we wanna extract content beginning from the first Heading 2 text
    to the last line before the next Heading 2 text
    """

    pattern_to_match = "## [v"

    count = 0
    lines = []
    heading_text = "## What's changed in this release\n"
    lines.append(heading_text)

    with open("CHANGELOG.md", "r") as c:
        for line in c:
            if pattern_to_match in line and count == 0:
                count += 1
            elif pattern_to_match not in line and count == 1:
                lines.append(line)
            elif pattern_to_match in line and count == 1:
                break

    # home = str(Path.home())
    # release_notes = os.path.join(home, "LATEST_RELEASE_NOTES.md")
    release_notes = os.path.join("../", "LATEST_RELEASE_NOTES.md")
    with open(release_notes, "w") as f:
        print("".join(lines), file=f, end="")


@task(
    help={
        "env_file": "Path to environment file (default: bin/.deploy.env)",
        "skip_deploy": "Setup infrastructure but don't deploy code",
    }
)
def deploy(c, env_file="bin/.deploy.env", skip_deploy=False):
    """
    Deploy the application to Dokku
    """
    # Ensure the env file exists
    env_path = Path(env_file)
    if not env_path.exists():
        print(f"❌ Environment file not found: {env_path}")
        print(f"💡 Copy bin/.deploy.env.example to {env_path} and fill in your values")
        return

    # Set SKIP_DEPLOY in the environment if requested
    env = {}
    if skip_deploy:
        env["SKIP_DEPLOY"] = "true"

    # Run the deployment script
    deploy_script = Path("bin/deploy.sh")
    if not deploy_script.exists():
        print(f"❌ Deployment script not found: {deploy_script}")
        return

    # Make deploy.sh executable if it's not already
    if not os.access(deploy_script, os.X_OK):
        c.run(f"chmod +x {deploy_script}")

    # Run the deployment script with the specified env file
    cmd = f"{deploy_script} --env-file={env_path.absolute()}"
    c.run(cmd, env=env, pty=True)
