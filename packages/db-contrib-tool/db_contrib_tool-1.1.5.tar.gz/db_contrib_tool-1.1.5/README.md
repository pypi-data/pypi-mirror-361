# db-contrib-tool

The `db-contrib-tool` - MongoDB's tools for contributors.

## Table of contents

- [db-contrib-tool](#db-contrib-tool)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributor's Guide (local development)](#contributors-guide-local-development)
    - [Install project dependencies](#install-project-dependencies)
    - [Run command line tool (local development)](#run-command-line-tool-local-development)
    - [Run linters](#run-linters)
    - [Run tests](#run-tests)
    - [Pre-commit](#pre-commit)
    - [Testing changes in mongo](#testing-changes-in-mongo)
    - [Testing changes locally](#testing-changes-locally)
    - [Versioning](#versioning)
    - [Code Review](#code-review)
    - [Deployment](#deployment)

## Description

The command line tool with various subcommands:
- `bisect`
  - [README.md](src/db_contrib_tool/evg_aware_bisect/README.md)
  - performs an evergreen-aware git-bisect to find the 'last passing version' and 'first failing version' of mongo
- `setup-repro-env`
  - [README.md](src/db_contrib_tool/setup_repro_env/README.md)
  - downloads and installs:
    - particular MongoDB versions
    - debug symbols
    - artifacts (including resmoke, python scripts etc)
    - python venv for resmoke, python scripts etc
- `symbolize`
  - [README.md](src/db_contrib_tool/symbolizer/README.md)
  - Symbolizes stacktraces from recent `mongod` and `mongos` binaries compiled in Evergreen, including patch builds, mainline builds, and release/production builds.
  - Requires authenticating to an internal MongoDB symbol mapping service.

## Dependencies

- Python 3.9 or later (python3 from the [MongoDB Toolchain](https://github.com/10gen/toolchain-builder/blob/master/INSTALL.md) is highly recommended)

## Installation

Make sure [dependencies](#dependencies) are installed.
Use [pipx](https://pypa.github.io/pipx/) to install db-contrib-tool that will be available globally on your machine:

```bash
python3 -m pip install pipx
python3 -m pipx ensurepath
```

Installing db-contrib-tool:

```bash
python3 -m pipx install db-contrib-tool
```

Upgrading db-contrib-tool:

```bash
python3 -m pipx upgrade db-contrib-tool
```

In case of installation errors, some of them may be related to pipx and could be fixed by re-installing pipx.

Removing pipx completely (WARNING! This will delete everything that is installed and managed by pipx):

```bash
python3 -m pip uninstall pipx
rm -rf ~/.local/pipx  # in case you're using the default pipx home directory
```

Now you can try to install again from scratch.

## Usage

Print out help message:

```bash
db-contrib-tool --help
```

For more information see [description](#description) section.

## Contributor's Guide (local development)

### Install project dependencies

This project uses [poetry](https://python-poetry.org/) for dependency management.

```bash
poetry install
```

### Run command line tool (local development)

Some subcommands like `bisect` and `symbolize` could be tested from the db-contrib-tool repo root:

```bash
poetry run db-contrib-tool --help
```

For `setup-repro-env` some features can also be tested from the db-contrib-tool repo root,
but full features are available when running from mongo repo root.
See [testing changes locally](#testing-changes-locally) section.

### Run linters

```bash
poetry run ruff format
poetry run ruff check
```

### Run tests

```bash
poetry run pytest
```

### Pre-commit

This project has [pre-commit](https://pre-commit.com/) configured. Pre-commit will run
configured checks at git commit time.<br>
To enable pre-commit on your local repository run:
```bash
poetry run pre-commit install
```

To run pre-commit manually:
```bash
poetry run pre-commit run
```
or across all files (not just those staged):
```bash
poetry run pre-commit run --all-files
```

### Testing changes in mongo

This tool is used to help run tests in the mongodb/mongo repository. On occasion, it may be
desirable to run a mongodb-mongo-* patch build with in-flight changes to this repository. The
following steps can be taken to accomplish that.

- Create a patch build with the changes you wish to test, running the `create_pyinstaller_binary` tasks.
- In the `mongo` repository, edit [evergreen/download_db_contrib_tool.py](https://github.com/10gen/mongo/blob/2a3cf647ce2b4e64d8b5001f50e00620114425c8/evergreen/download_db_contrib_tool.py#L17) to use your patch's Evergreen
version, like `https://mdb-build-public.s3.amazonaws.com/db-contrib-tool-binaries/<your patch's version ID>/"`

### Testing changes locally

Pipx installation recommendations can be found in [installation](#installation) section.

The tool can be installed via pipx from your local repo:

```bash
python3 -m pipx install /path/to/db-contrib-tool/repo/root/dir
```

If the tool is already installed you can force install an updated version using --force flag:

```bash
python3 -m pipx install --force /path/to/db-contrib-tool/repo/root/dir
```

After these steps you can run in-development version of db-contrib-tool from any directory:

```bash
db-contrib-tool --help
```

### Versioning

This project uses [semver](https://semver.org/) for versioning.
Please include a description what is added for each new version in `CHANGELOG.md`.

### Code Review

This projects uses GitHub PRs for code reviews. You should assign any reviewers you would like to look at the PR to it.

This project uses the GitHub merge queue. Click "Merge when ready" as soon as you'd like.

### Deployment

Deployment to pypi is done by [deploy](https://spruce.mongodb.com/commits/db-contrib-tool?taskNames=deploy)
task of `db-contrib-tool` project in Evergreen.
A new version in Evergreen is created on merges to `main` branch.
