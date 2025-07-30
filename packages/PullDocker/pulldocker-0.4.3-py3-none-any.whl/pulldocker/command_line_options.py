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

import argparse
import logging

from .constants import APP_NAME, APP_VERSION, APP_DESCRIPTION


class CommandLineOptions(object):
    """
    Parse command line arguments
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog=f'{APP_NAME}',
                                              description=APP_DESCRIPTION)
        self.parser.set_defaults(verbose_level=logging.INFO)
        self.parser.add_argument('-V',
                                 '--version',
                                 action='version',
                                 version=f'{APP_NAME} v{APP_VERSION}')
        self.parser.add_argument('-v',
                                 '--verbose',
                                 dest='verbose_level',
                                 action='store_const',
                                 const=logging.DEBUG,
                                 help='Show diagnostic information messages')
        self.parser.add_argument('-q',
                                 '--quiet',
                                 dest='verbose_level',
                                 action='store_const',
                                 const=logging.ERROR,
                                 help='Show only error messages')

    def add_group(self, name: str) -> argparse._ArgumentGroup:
        """
        Add a command-line options group

        :param name: name for the new group
        :return: _ArgumentGroup object with the new command-line options group
        """
        return self.parser.add_argument_group(name)

    def add_configuration_arguments(self) -> None:
        """
        Add configuration command-line options
        """
        group = self.add_group('Configuration')
        group.add_argument('--configuration',
                           required=True,
                           type=str,
                           help='configuration file')

    def add_configuration_watch(self) -> None:
        """
        Add configuration command-line options
        """
        group = self.add_group('Watch mode')
        group.add_argument('--watch',
                           required=False,
                           action='store_true',
                           default=False,
                           help='Watch for changes')
        group.add_argument('--sleep',
                           required=False,
                           type=int,
                           default=60,
                           help='Sleep time while watching')

    def parse_options(self) -> argparse.Namespace:
        """
        Parse command-line options

        :return: command-line options
        """
        self.options = self.parser.parse_args()
        # Check for missing options
        if not any(vars(self.options).values()):
            self.parser.print_help()
            self.parser.exit(1)
        return self.options
