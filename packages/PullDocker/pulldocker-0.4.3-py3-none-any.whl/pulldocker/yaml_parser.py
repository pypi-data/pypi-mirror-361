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

import yaml

from pulldocker.profile import Profile

ATTRIBUTES_FROM_COMMON = ('status', 'directory', 'remotes', 'tags_regex',
                          'compose_file', 'detached', 'build', 'recreate',
                          'progress', 'compose_executable', 'command',
                          'commands_before', 'commands_after',
                          'commands_begin', 'commands_end')
DEFAULT_ATTRIBUTES = {
    'status': True,
    'detached': True,
    'build': False,
    'recreate': False,
    'progress': True,
}


class YamlParser(object):
    def __init__(self, filename: str):
        self.profiles = {}
        self.common_profile = None
        with open(filename, 'r') as file:
            values = {item['NAME']: item
                      for item in yaml.load_all(stream=file,
                                                Loader=yaml.Loader)
                      if item}
        # Load profiles
        for name, values in values.items():
            profile = Profile(
                name=name,
                status=values.get('STATUS'),
                directory=values.get('REPOSITORY_DIR'),
                remotes=values.get('REMOTES'),
                tags_regex=values.get('TAGS'),
                compose_file=values.get('COMPOSE_FILE'),
                detached=values.get('DETACHED'),
                build=values.get('BUILD'),
                recreate=values.get('RECREATE'),
                progress=values.get('PROGRESS'),
                compose_executable=values.get('COMPOSE_EXEC'),
                command=values.get('COMMAND'),
                commands_before=values.get('BEFORE'),
                commands_after=values.get('AFTER'),
                commands_begin=values.get('BEGIN'),
                commands_end=values.get('END'),
            )
            if values.get('COMMON', False):
                # Set the profile as the new common profile
                self.common_profile = profile
            else:
                if common_profile := self.common_profile:
                    # Restore attributes from common profile
                    for attribute in ATTRIBUTES_FROM_COMMON:
                        if getattr(profile, attribute) in (None, []):
                            setattr(profile,
                                    attribute,
                                    getattr(common_profile, attribute))
                # Set default attributes
                for attribute, default_value in DEFAULT_ATTRIBUTES.items():
                    if getattr(profile, attribute) is None:
                        setattr(profile, attribute, default_value)
                # Save profile
                self.profiles[name] = profile

    def get_profiles(self) -> list[Profile]:
        """
        Return the configuration profiles

        :return: profiles list
        """
        return list(self.profiles.values())
