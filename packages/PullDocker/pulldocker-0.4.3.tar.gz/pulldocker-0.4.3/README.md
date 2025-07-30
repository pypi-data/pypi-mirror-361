# PullDocker

[![Travis CI Build Status](https://img.shields.io/travis/com/muflone/pulldocker/main.svg)](https://www.travis-ci.com/github/muflone/pulldocker)
[![CircleCI Build Status](https://img.shields.io/circleci/project/github/muflone/pulldocker/main.svg)](https://circleci.com/gh/muflone/pulldocker)
[![Python 3.10](https://github.com/muflone/pulldocker/actions/workflows/python-3.10.yml/badge.svg)](https://github.com/muflone/pulldocker/actions/workflows/python-3.10.yml)
[![Python 3.11](https://github.com/muflone/pulldocker/actions/workflows/python-3.11.yml/badge.svg)](https://github.com/muflone/pulldocker/actions/workflows/python-3.11.yml)
[![Python 3.12](https://github.com/muflone/pulldocker/actions/workflows/python-3.12.yml/badge.svg)](https://github.com/muflone/pulldocker/actions/workflows/python-3.12.yml)
[![Python 3.13](https://github.com/muflone/pulldocker/actions/workflows/python-3.13.yml/badge.svg)](https://github.com/muflone/pulldocker/actions/workflows/python-3.13.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/PullDocker.svg)](https://pypi.org/project/PullDocker/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PullDocker.svg)](https://pypi.org/project/PullDocker/)

**Description:** Watch git repositories for Docker compose configuration changes

**Copyright:** 2024-2025 Fabio Castelli (Muflone) <muflone@muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/pulldocker

**Documentation:** http://www.muflone.com/pulldocker/

## Description

PullDocker is a command line tool monitor a git repository for changes and run
`docker deploy` (and optionally other commands) when changes are detected.

This tool comes handy to automate Docker compose deployments on git operations
(gitops) and can automatically deployments every time a repository receives
updates or a new tag is made.

## System Requirements

* Python >= 3.10
* PyYAML 6.0.x (https://pypi.org/project/PyYAML/)
* GitPython 3.1.x (https://pypi.org/project/GitPython/)

## Usage

PullDocker is a command line utility, so it requires some arguments to be
specified when executing it:

```
pulldocker
  --configuration <YAML FILE>
  [--verbose | --quiet]
  [--watch] [--sleep <SECONDS>]
```

The argument `--configuration` refers to a YAML configuration file containing
repositories' specifications (see below).

The argument `--verbose` will show additional debug messages for diagnostic
purposes.

The argument `--quiet` will hide every diagnostic message showing only errors.

The argument `--watch` will enable the watch mode, continuously checking the
repository for changes.

The argument `--sleep` can specify a number of seconds to await in watch mode
between each iteration.

## YAML Configuration specifications

A YAML configuration file consists of one or more repositories, separated using
`---` and a newline. A repository will require the following minimum arguments:

```yaml
NAME: Repository name
REPOSITORY_DIR: <Path where the git repository is cloned and can be pull>
REMOTES:
  - Remotes list from where to pull the new commits
```

Some more advanced specifications can be found below.

### Minimal example file

```yaml
NAME: PullDocker
REPOSITORY_DIR: /home/muflone/pulldocker.git
REMOTES:
  - origin
```

The previous example would monitor the /home/muflone/pulldocker.git repository,
and it will pull new commits from the remote called `origin`.

Whenever a new commit is found, a new ```docker compose up -d``` command will be
issued in the repository directory.

### Multiple repositories specifications

Multiple repositories can be configured in the same YAML file, and they will be
monitored one after the other, sequentially.

A multi-repository file could be the following:

```yaml
NAME: PullDocker
REPOSITORY_DIR: /home/muflone/pulldocker.git
REMOTES:
  - origin
---
NAME: PixelColor
REPOSITORY_DIR: /home/muflone/pixelcolor.git
REMOTES:
  - github
```

The first repository will monitor the `origin` remote and the second repository
will monitor the `github` remote.

### Common repository specifications

To avoid repeating in every repository the same values, you can define a
special default repository used to specify the default arguments for every
following repository.

When the `COMMON` argument is set to `true` such repository won't be processed
but its specifications will be used when another repository lacks the
specification.

For example, the following configuration will automatically set the default
arguments for both the repositories REPOSITORY1 and REPOSITORY2.

```yaml
NAME: DEFAULT
COMMON: true
STATUS: true
REMOTES:
  - origin
COMPOSE_FILE: docker-compose.yaml
BUILD: false
RECREATE: true
PROGRESS: false
---
NAME: REPOSITORY1
REPOSITORY_DIR: /home/muflone/repository1
BUILD: true
---
NAME: REPOSITORY2
REPOSITORY_DIR: /home/muflone/repository2
RECREATE: false
```

Both repositories will inherit the arguments from the repository named DEFAULT
which has the `COMMON` argument set.

In particular the repository named REPOSITORY1 will override to `true` the
default `BUILD` argument which was set to `false` in the default repository.

Similarly, the repository named REPOSITORY2 will override to `false` the
default `RECREATE` argument which was set to `true` in the default repository.

### Complete YAML specifications

Here follows the complete YAML specifications for using PullDocker:

```yaml
NAME: Repository name
COMMON: false
STATUS: true
REPOSITORY_DIR: <Path where the git repository is cloned and can be pull>
REMOTES:
  - origin
  - github
  - gitlab
TAGS: '*'
COMPOSE_FILE: docker/docker-compose.yaml
COMPOSE_EXEC:
  - docker
  - compose
DETACHED: true
BUILD: true
RECREATE: true
PROGRESS: true
COMMAND: docker compose -f docker/docker-compose.yaml up -d
BEGIN:
  - bash -c 'echo BEGIN ${DATE} ${TIME}'
BEFORE:
  - bash -c 'echo BEFORE ${DATE} ${TIME}'
  - bash -c 'echo ${TAG} ${TAG_HASH} ${TAG_DATE} ${TAG_TIME}'
AFTER:
  - bash -c 'echo AFTER ${DATE} ${TIME}'
  - bash -c 'echo ${TAG} ${TAG_HASH} ${TAG_DATE} ${TAG_TIME}'
END:
  - bash -c 'echo END ${DATE} ${TIME}'
```

The `NAME` argument is required for each repository and identifies the
repository itself. Its usage becomes useful on the commands, and it's assigned
to the NAME command variable (see below).

The `COMMON` argument can be set to `true` to define whether the repository
will be used as a default repository for the next repositories in the same
file. Any arguments not explicitly set in the repository will be inherited
from the latest repository having the `COMMON` argument set to `true`.

This means you could have many repositories with `COMMON` set to `true` and
their arguments will be used for the next repositories in the same YAML file.

The `STATUS` argument can be a boolean value with `true` or `false` and if set
to `false` the repository is considered as disabled so it will not be checked
or updated.
This could be useful to disable the repository and still keeping its
definition in the YAML file.

The `REPOSITORY_DIR` argument is used to specify to git working copy to update
and to check for updates.

The `REMOTES` arguments is a list with the remotes to check for updates, as
previously set in the git directory.

The `TAGS` argument can be used to deploy the update only when the latest
commit matches a tag. The tag specification can be `'*'` to indicate any tag
available or a *regex* (Regular expression) can be used to match the available
tags. For example, the following: `TAGS: '0\.[1-9]\.*'` will only match the
tags starting with 0.1.x up to 0.9.x, and it would exclude the tags with 0.0.x.

If no tags are specified, any available commit newer than the current commit
will issue the deployment.

The `COMPOSE_FILE` argument is used to specify the path for a
docker-compose.yaml/yml file in the case the file is contained in another
directory, or it has a different name than the default docker-compose.yaml.

The `COMPOSE_EXEC` argument is used to specify the default `docker compose` to
execute to deploy the container. This defaults to `docker compose` command but
any other command can be specified. Please note this is a **list** of strings,
not a single string.

The `DETACHED` argument is used to specify a boolean value for running the
docker compose in detached mode (the default, passing `true`) or without the
detached mode, by specifying the value `false`.

The `BUILD` argument is used to build the images before starting the
deployment.

The `RECREATE` argument is used to force the recreation of the containers even
if the configuration wasn't changed.

The `PROGRESS` argument is used to enable or disable the progress output
during the deployment.

The `COMMAND` argument can be used to specify the explicit command for the
deployment, instead of using `docker compose up`. This command will override
any previous `COMPOSE_FILE`, `DETACHED`, `BUILD`, `RECREATE`, `PROGRESS`
arguments.

To avoid doing any deployment, you can use the command `true` or `false` which
does nothing and exit immediately after.

The `BEGIN` argument can be a list of commands to execute when checking the
status for the repository, regardless if it has updates or not.
Multiple commands can be specified.

The `BEFORE` argument can be a list of commands to execute after checking the
status for the repository, before the deployment is done if it **has updates**.
Multiple commands can be specified.

The `AFTER` argument can be a list of commands to execute after checking the
status for the repository, after the deployment is done if it **has updates**.
Multiple commands can be specified.

The `END` argument can be a list of commands to execute after checking the
status for the repository, regardless if it has updates or not.
Multiple commands can be specified.

### Command details

The commands' arguments can use both strings (one command per line) or list of
arguments (one argument per line) using the YAML lists syntax.

The following are both valid:

```yaml
BEGIN:
  - bash -c 'echo BEGIN ${DATE} ${TIME}'
```

Using the list syntax:

```yaml
BEGIN:
  -
    - bash
    - -c
    - 'echo BEGIN ${DATE} ${TIME}'
```

### Command variables

The following special variables can be used in any command to replace the
variable with its value:

- `${NAME}`: repository name in the YAML file
- `${DIRECTORY}`: repository directory path
- `${DATE}`: current date with the format YYYY-MM-DD
- `${TIME}`: current time with the format HH:mm:ss
- `${COMMIT_HASH}`: latest commit hash
- `${COMMIT_DATE}`: latest commit date with the format YYYY-MM-DD
- `${COMMIT_TIME}`: latest commit with the format HH:mm:ss
- `${COMMIT_BRANCH}`: latest commit branch name
- `${COMMIT_AUTHOR}`: latest commit author name
- `${COMMIT_EMAIL}`: latest commit author email
- `${COMMIT_MESSAGE}`: latest commit message
- `${COMMIT_SUMMARY}`: latest commit summary
- `${COMMITS_COUNT}`: number of commits

The following variables can only be used for the `COMMAND`, `BEFORE` and
`AFTER` arguments when the `TAGS` argument is used so their values will refer
to the matching tag used:

- `${TAG}`: tag name
- `${TAG_HASH}`: commit hash for the matching tag
- `${TAG_AUTHOR}`: commit author name for the matching tag
- `${TAG_EMAIL}`: commit author email for the matching tag
- `${TAG_MESSAGE}`: tag message
- `${TAG_SUMMARY}`: commit message for the matching tag
- `${TAG_DATE}`: tag date with the format YYYY-MM-DD
- `${TAG_TIME}`: tag time with the format HH:mm:ss

### Commands output formatting

To get a compact and constant output using the commmands, you can benefit from
using the printf width specifiers and pass the matching values as variables

```yaml
BEGIN:
  - printf '${DATE} ${TIME} %-15s BEGIN  %-4d ${COMMIT_HASH} ${COMMIT_DATE} ${COMMIT_TIME} > ${COMMIT_SUMMARY}\n' '${NAME}' '${COMMITS_COUNT}'
BEFORE:
  - printf '${DATE} ${TIME} %-15s BEFORE %-4d ${COMMIT_HASH} ${COMMIT_DATE} ${COMMIT_TIME} > Deploying update...\n' '${NAME}' '${COMMITS_COUNT}'
AFTER:
  - printf '${DATE} ${TIME} %-15s AFTER  %-4d ${COMMIT_HASH} ${COMMIT_DATE} ${COMMIT_TIME} > Deployment completed\n' '${NAME}' '${COMMITS_COUNT}'
END:
  - printf '${DATE} ${TIME} %-15s END    %-4d ${COMMIT_HASH} ${COMMIT_DATE} ${COMMIT_TIME} > ${COMMIT_SUMMARY}\n' '${NAME}' '${COMMITS_COUNT}'
```

The previous commands will output the current date and time, followed by the
repository name with a fixed width of 15 characters (note the usage of `{NAME}`
at the end of the printf command).

After that follows the commands' phase (BEGIN, BEFORE, AFTER and END), then
four digits for the commits' count (note the usage of `${COMMITS_COUNT}` at
the end of the printf command).

Following, you can find the commit hash identifier, date and time and the
variable length commit summary or a pre-defined text for the `BEFORE` and
`AFTER` commands phases.

The output will be similar to:

```text
2025-07-13 03:25:40 REPOSITORY1     BEGIN  22   df2fcc374a2d94fcbf09c881a373029c299766e3 2024-12-05 23:31:50 > Removed secret
2025-07-13 03:25:41 REPOSITORY1     BEFORE 23   dc7b3fe472382f1ef7cc7d749018f6b213c7bf14 2024-12-05 23:32:17 > Deploying update...
2025-07-13 03:25:41 REPOSITORY1     AFTER  23   dc7b3fe472382f1ef7cc7d749018f6b213c7bf14 2024-12-05 23:32:17 > Deployment completed
2025-07-13 03:25:41 REPOSITORY1     END    23   dc7b3fe472382f1ef7cc7d749018f6b213c7bf14 2024-12-05 23:32:17 > Removed secret
```

For the best results, you could use the `--quiet` command-line option to hide
all diagnostic messages except the error messages.

You can freely apply any changes to the commands` format to get your desired
output.
