"""Module keeps all git related classes and methods.
"""
import json
import logging
import pathlib
import re

import git
import yaml
from git.objects import Commit

logger = logging.getLogger(__name__)


class GitClient:
    """
    Client for any operation regarding the underlying git repository
    """

    def __init__(self, model_root_path: pathlib.Path, git_tag_regex: str) -> None:
        """
        Inits a new git client.
        """
        self.git_tag_regex = git_tag_regex
        self.model_root_path = model_root_path
        self.repository = git.Repo(str(self.model_root_path))

    def _get_commit_from_tag(self) -> Commit:
        """
        Evaluates the changes found in the solution git repository
        and returns a collection of changes with meta information.

        Will take latest commit that matches git_tag_regex as first commit.
        Will take current commit as last commit.
        """
        tags_sorted = sorted(
            self.repository.tags, key=lambda t: t.commit.committed_datetime
        )
        commit_start: Commit | None = None
        for tag in reversed(tags_sorted):
            if re.search(self.git_tag_regex, tag.name):
                commit_start = tag.commit
                break
        if commit_start is None:
            logger.error(
                "Git mode requires at least one tag with format [ '%s' ]",
                self.git_tag_regex,
            )
            raise ValueError(
                (
                    "Git mode requires at least one tag with"
                    f" format [ '{self.git_tag_regex}' ]"
                )
            )
        logger.info("Commit found: %s", commit_start)
        return commit_start

    def get_git_tree_list(
        self, commit_start: Commit, target_path: pathlib.Path
    ) -> list:
        # Retrieve list of files at the specified commit
        git_file_list = self.repository.git.ls_tree(commit_start, r=True).split("\n")
        git_files = [line.split("\t")[1] for line in git_file_list if line]
        # if target path is the root path
        if target_path == pathlib.Path(""):
            return git_files
        # make path relative to the git repository root if it isn't
        if (
            self.repository.working_tree_dir is not None
            and str(self.repository.working_tree_dir) in target_path.as_posix()
        ):
            target_path = target_path.relative_to(
                pathlib.Path(self.repository.working_tree_dir)
            )
        # add trailing slashes to enable exact match
        filter_path = target_path.as_posix()
        if target_path.is_dir():
            filter_path = f"{target_path}/"
        filtered_files = [
            file_path for file_path in git_files if file_path.startswith(filter_path)
        ]
        return filtered_files

    def get_json_from_tag(self, target_path: pathlib.Path) -> dict[str, dict | list]:
        """
        Wrapper function for _get_commit_from_tag. Gets commit based on
        regex and transforms json to dict.
        """
        commit_start = self._get_commit_from_tag()
        path_to_json: dict[str, dict | list] = {}
        git_files = self.get_git_tree_list(commit_start, target_path)

        for git_file in git_files:
            if git_file.endswith(".json"):
                git_cmd = f"{commit_start}:{git_file}"
                file_content = json.loads(self.repository.git.show(git_cmd))
                path_to_json[git_file] = file_content
        return path_to_json

    def get_yaml_from_tag(self, target_path: pathlib.Path) -> dict[str, dict | list]:
        """
        Wrapper function for _get_commit_from_tag. Gets commit based on
        regex and transforms yaml to dict.
        """
        commit_start = self._get_commit_from_tag()
        path_to_yaml: dict[str, dict | list] = {}
        git_files = self.get_git_tree_list(commit_start, target_path)

        for git_file in git_files:
            if git_file.endswith(".yaml") or git_file.endswith(".yml"):
                git_cmd = f"{commit_start}:{git_file}"
                file_content = yaml.safe_load(self.repository.git.show(git_cmd))
                path_to_yaml[git_file] = file_content
        return path_to_yaml
