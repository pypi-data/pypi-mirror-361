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

from .tag import Tag

from git import Repo


class Repository():
    def __init__(self, directory: str):
        self.directory = directory

        # Load repository
        self._repository = Repo(self.directory)

    def find_head(self) -> None:
        self._head = self._repository.head
        self._commit = self._head.commit

    def get_hash(self) -> str:
        """
        Get the latest commit hash

        :return: commit hash
        """
        return self._commit.hexsha

    def get_author(self) -> str:
        """
        Get the latest commit author name

        :return: commit author name
        """
        return self._commit.author.name

    def get_email(self) -> str:
        """
        Get the latest commit author email

        :return: commit author email
        """
        return self._commit.author.email

    def get_datetime(self) -> str:
        """
        Get the latest commit date and time

        :return: commit datetime
        """
        return self._commit.authored_datetime

    def get_message(self) -> str:
        """
        Get the text from the latest commit

        :return: commit description
        """
        return self._commit.message

    def get_summary(self) -> str:
        """
        Get the summary text from the latest commit

        :return: commit summary
        """
        return self._commit.summary

    def get_branch(self) -> str:
        """
        Get the branch name from the HEAD

        :return: branch name
        """
        return self._head.reference.name

    def get_remotes(self) -> list[str]:
        """
        Get the list of remotes

        :return: list of remotes
        """
        return [remote.name for remote in self._repository.remotes]

    def get_commits_count(self) -> int:
        """
        Get the total number of commits in the repository

        :return: number of commits
        """
        return len(list(self._repository.iter_commits()))

    def pull(self,
             remote: str,
             branch: str) -> None:
        """
        Pull the latest commit from remote

        :param remote: name of the remote
        :param branch: name of the branch
        """
        self._repository.remote(name=remote).pull(refspec=branch)

    def fetch(self,
              remote: str) -> None:
        """
        Get the latest metadata from remote

        :param remote: name of the remote
        """
        self._repository.remote(name=remote).fetch()

    def get_tags(self):
        """
        Return a list of tag names

        :return: list of tags
        """
        return [tag.name for tag in self._repository.tags]

    def get_tag(self,
                name: str) -> Tag:
        """
        Return a Tag object matching the specified tag name

        :param name: name of the tag
        :return: Tag object
        """
        tag = self._repository.tags[name]
        return Tag(name=tag.name,
                   hash=tag.commit.hexsha,
                   author=tag.commit.author.name,
                   email=tag.commit.author.email,
                   message=tag.tag.message if tag.tag else None,
                   date_time=tag.commit.authored_datetime,
                   summary=tag.commit.summary)
