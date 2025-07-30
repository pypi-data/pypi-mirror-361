##
#     Project: PullDocker
# Description: Watch git repositories for Docker compose configuration changes
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2024-2025 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

import datetime
import logging
import subprocess

from pulldocker.repository import Repository
from pulldocker.tag import Tag


class Profile():
    def __init__(self,
                 name: str,
                 status: bool,
                 directory: str,
                 remotes: list[str] = None,
                 tags_regex: str = None,
                 compose_file: str = None,
                 compose_executable: list[str] | str = None,
                 detached: bool = True,
                 build: bool = False,
                 recreate: bool = False,
                 progress: bool = True,
                 command: list[str] | str = None,
                 commands_before: list[list[str] | str] = None,
                 commands_after: list[list[str] | str] = None,
                 commands_begin: list[list[str] | str] = None,
                 commands_end: list[list[str] | str] = None,
                 ):
        self.name = name
        self.status = status
        self.remotes = remotes
        self.directory = directory
        self.repository = Repository(directory=directory)
        self.tags_regex = '.*' if tags_regex == '*' else tags_regex
        self.compose_file = compose_file
        self.compose_executable = compose_executable
        self.detached = detached
        self.build = build
        self.recreate = recreate
        self.progress = progress
        self.command = command
        self.commands_before = commands_before or []
        self.commands_after = commands_after or []
        self.commands_begin = commands_begin or []
        self.commands_end = commands_end or []

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name="{self.name}", '
                f'status={self.status}'
                ')')

    def _execute_commands(self,
                          commands: list[list[str] | str],
                          repository: Repository,
                          tag: Tag) -> None:
        """
        Execute commands

        :param repository: Repository object
        """
        now = datetime.datetime.now()
        replacements = {
            '${NAME}': self.name,
            '${DIRECTORY}': self.directory,
            '${DATE}': now.strftime('%Y-%m-%d'),
            '${TIME}': now.strftime('%H:%M:%S'),
            '${COMMIT_HASH}': repository.get_hash(),
            '${COMMIT_DATE}': repository.get_datetime().strftime('%Y-%m-%d'),
            '${COMMIT_TIME}': repository.get_datetime().strftime('%H:%M:%S'),
            '${COMMIT_BRANCH}': repository.get_branch(),
            '${COMMIT_AUTHOR}': repository.get_author(),
            '${COMMIT_EMAIL}': repository.get_email(),
            '${COMMIT_MESSAGE}': repository.get_message(),
            '${COMMIT_SUMMARY}': repository.get_summary(),
            '${COMMITS_COUNT}': str(repository.get_commits_count()),
        }
        if tag is not None:
            replacements['${TAG}'] = tag.name
            replacements['${TAG_AUTHOR}'] = tag.author
            replacements['${TAG_EMAIL}'] = tag.email
            replacements['${TAG_MESSAGE}'] = tag.message
            replacements['${TAG_SUMMARY}'] = tag.summary
            replacements['${TAG_HASH}'] = tag.hash
            replacements['${TAG_DATE}'] = tag.date_time.strftime('%Y-%m-%d')
            replacements['${TAG_TIME}'] = tag.date_time.strftime('%H:%M:%S')

        for command in commands:
            new_arguments = []
            for argument in (command
                             if isinstance(command, list)
                             else [command]):
                for key, value in replacements.items():
                    argument = argument.replace(
                        key,
                        value if value is not None else '')
                new_arguments.append(argument)
            subprocess.call(args=new_arguments,
                            shell=not isinstance(command, list),
                            cwd=self.directory)

    def begin(self,
              repository: Repository) -> None:
        """
        Execute commands at the beginning

        :param repository: Repository object
        """
        logging.debug('Executing commands for section BEGIN')
        self._execute_commands(commands=self.commands_begin,
                               repository=repository,
                               tag=None)

    def end(self,
            repository: Repository) -> None:
        """
        Execute commands at the end

        :param repository: Repository object
        """
        logging.debug('Executing commands for section END')
        self._execute_commands(commands=self.commands_end,
                               repository=repository,
                               tag=None)

    def before(self,
               repository: Repository,
               tag: Tag) -> None:
        """
        Execute commands before the deployment

        :param repository: Repository object
        :param tag: Tag object
        """
        logging.debug('Executing commands for section BEFORE')
        self._execute_commands(commands=self.commands_before,
                               repository=repository,
                               tag=tag)

    def after(self,
              repository: Repository,
              tag: Tag) -> None:
        """
        Execute commands after the deployment

        :param repository: Repository object
        :param tag: Tag object
        """
        logging.debug('Executing commands for section AFTER')
        self._execute_commands(commands=self.commands_after,
                               repository=repository,
                               tag=tag)

    def execute(self,
                repository: Repository,
                tag: Tag) -> None:
        """
        Execute commands from the profile

        :param repository: Repository object
        :param tag: Tag object
        """
        # Execute deployment command
        logging.debug('Executing deploy command')
        if self.command:
            arguments = self.command
        else:
            if self.compose_executable:
                # Use custom docker compose command
                if isinstance(self.compose_executable, str):
                    arguments = [self.compose_executable]
                else:
                    arguments = self.compose_executable
            else:
                # Use default docker compose command
                arguments = ['docker', 'compose']
            if self.compose_file:
                arguments.extend(['-f', self.compose_file])
            if not self.progress:
                arguments.extend(['--progress', 'quiet'])
            arguments.append('up')
            if self.detached:
                arguments.append('-d')
            if self.build:
                arguments.append('--build')
            if self.recreate:
                arguments.append('--force-recreate')
        self._execute_commands(commands=[arguments],
                               repository=repository,
                               tag=tag)
