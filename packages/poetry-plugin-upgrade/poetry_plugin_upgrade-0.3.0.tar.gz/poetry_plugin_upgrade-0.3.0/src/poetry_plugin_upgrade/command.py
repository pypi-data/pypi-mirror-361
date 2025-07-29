from collections.abc import Iterable
from http import HTTPStatus
from typing import Any

import requests
from cleo.helpers import argument, option
from poetry.console.commands.installer_command import InstallerCommand
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.dependency_group import DependencyGroup
from poetry.core.packages.package import Package
from poetry.version.version_selector import VersionSelector
from tomlkit import dumps
from tomlkit.toml_document import TOMLDocument


class UpgradeCommand(InstallerCommand):
    name = "upgrade"
    description = "Update dependencies and bump versions in <comment>pyproject.toml</>"

    arguments = [
        argument(
            name="packages",
            description="The packages to update.",
            optional=True,
            multiple=True,
        )
    ]

    options = [
        *InstallerCommand._group_dependency_options(),  # noqa: SLF001
        option(
            long_name="latest",
            short_name=None,
            description="Update to latest available compatible versions.",
        ),
        option(
            long_name="pinned",
            short_name=None,
            description=(
                "Include pinned (exact) dependencies when updating to latest."
            ),
        ),
        option(
            long_name="exclude",
            short_name=None,
            description="Exclude dependencies.",
            multiple=True,
            flag=False,
        ),
        option(
            long_name="no-install",
            short_name=None,
            description="Do not install dependencies, only refresh "
            "<comment>pyproject.toml</> and <comment>poetry.lock</>.",
        ),
        option(
            long_name="dry-run",
            short_name=None,
            description="Output bumped <comment>pyproject.toml</> but do not "
            "execute anything.",
        ),
        option(
            long_name="preserve-wildcard",
            short_name=None,
            description="Do not bump wildcard dependencies " "when updating to latest.",
        ),
    ]

    def handle(self) -> int:
        only_packages = self.argument("packages")
        latest = self.option("latest")
        pinned = self.option("pinned")
        no_install = self.option("no-install")
        dry_run = self.option("dry-run")
        exclude = self.option("exclude")
        preserve_wildcard = self.option("preserve-wildcard")

        if pinned and not latest:
            self.line_error("'--pinned' specified without '--latest'")
            raise Exception

        if preserve_wildcard and not latest:
            self.line_error("'--preserve-wildcard' specified without '--latest'")
            raise Exception

        selector = VersionSelector(self.poetry.pool)
        pyproject_content = self.poetry.file.read()
        original_pyproject_content = self.poetry.file.read()

        for group in self.get_groups():
            for dependency in group.dependencies:
                self.handle_dependency(
                    dependency=dependency,
                    latest=latest,
                    pinned=pinned,
                    only_packages=only_packages,
                    pyproject_content=pyproject_content,
                    selector=selector,
                    exclude=exclude,
                    preserve_wildcard=preserve_wildcard,
                )

        if dry_run:
            self.line(dumps(pyproject_content))
            return 0

        # write new content to pyproject.toml
        self.poetry.file.write(pyproject_content)
        self.reset_poetry()

        try:
            if no_install:
                # update lock file
                self.call(name="lock", args="--no-update")
            else:
                # update dependencies
                self.call(name="update")
        except Exception as e:
            self.line("\nReverting <comment>pyproject.toml</>")
            self.poetry.file.write(original_pyproject_content)
            raise e

        return 0

    def get_groups(self) -> Iterable[DependencyGroup]:
        """Returns activated dependency groups"""

        for group in self.activated_groups:
            yield self.poetry.package.dependency_group(group)

    @staticmethod
    def retrieve_latest_version(name: str) -> str | None:
        """Retrieve the latest version of a package from PyPI"""

        response: requests.Response = requests.get(
            f"https://pypi.org/pypi/{name}/json", timeout=10
        )

        if response.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_FOUND):
            response.raise_for_status()

        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        info = response.json().get("info")

        return info["version"]

    def handle_dependency(
        self,
        dependency: Dependency,
        latest: bool,
        pinned: bool,
        only_packages: list[str],
        pyproject_content: TOMLDocument,
        selector: VersionSelector,
        exclude: list[str],
        preserve_wildcard: bool,
    ) -> None:
        """Handle dependency update based on options

        Determines if a dependency can be bumped in pyproject.toml
        and calls bump_version_in_pyproject_content() if it can.
        """

        if not self.is_bumpable(
            dependency,
            only_packages,
            latest,
            pinned,
            exclude,
            preserve_wildcard,
        ):
            return

        target_package_version = "*" if latest else dependency.pretty_constraint
        candidate: Package | None = selector.find_best_candidate(
            package_name=dependency.name,
            target_package_version=target_package_version,
            allow_prereleases=dependency.allows_prereleases(),
            source=dependency.source_name,
        )

        if candidate is None:
            self.line(f"No new version for '{dependency.name}'")
            return

        new_version = self.handle_version(
            current_version=dependency.pretty_constraint, candidate=candidate
        )

        self.bump_version_in_pyproject_content(
            dependency=dependency,
            new_version=new_version,
            pyproject_content=pyproject_content,
        )

    @staticmethod
    def handle_version(current_version: str, candidate: Package) -> str:
        """Handle version based on original version"""

        if current_version[0] == "<":
            return current_version

        version_constraint: str | None = None

        # preserve zero based carets ('^0.0') when bumping to latest
        if current_version[0] == "^":
            version_constraint = "^"

        if current_version[0] == "~" and "." in current_version:
            version_constraint = "~"

        if current_version.startswith(">="):
            version_constraint = ">="
        elif current_version[0] == ">":
            version_constraint = ">"

        if current_version.startswith("=="):
            version_constraint = "=="

        return (
            f"{version_constraint}{candidate.pretty_version}"
            if version_constraint
            else candidate.pretty_version
        )

    @staticmethod
    def is_bumpable(
        dependency: Dependency,
        only_packages: list[str],
        latest: bool,
        pinned: bool,
        exclude: list[str],
        preserve_wildcard: bool,
    ) -> bool:
        """Determines if a dependency can be bumped in pyproject.toml"""

        constraint = dependency.pretty_constraint

        if is_bumping_prevented(dependency=dependency, exclude=exclude):
            return False

        # check if dependency is in only_packages
        if only_packages and dependency.name not in only_packages:
            return False

        if preserve_wildcard and is_wildcard(version=constraint):
            return False

        if not latest and any(
            [
                not pinned and is_pinned(version=constraint),
                is_wildcard(version=constraint),
                is_less_than_or_equal_to(version=constraint),
                is_less_than(version=constraint),
                is_greater_than(version=constraint),
                is_not_equal(version=constraint),
                is_multiple_requirements(version=constraint),
            ]
        ):
            return False

        return pinned or not is_pinned(constraint)

    @staticmethod
    def bump_version_in_pyproject_content(
        dependency: Dependency,
        new_version: str,
        pyproject_content: TOMLDocument,
    ) -> None:
        """Bumps versions in pyproject content (pyproject.toml)"""

        poetry_content: dict[str, Any] = pyproject_content.get("tool", {}).get(
            "poetry", {}
        )

        for group in dependency.groups:
            # find section to modify
            section = {}

            if group == "main":
                section = poetry_content.get("dependencies", {})
            elif group == "dev" and "dev-dependencies" in poetry_content:
                # take account for the old `dev-dependencies` section
                section = poetry_content.get("dev-dependencies", {})
            else:
                section = (
                    poetry_content.get("group", {})
                    .get(group, {})
                    .get("dependencies", {})
                )

            # modify section
            if isinstance(section.get(dependency.pretty_name), str):
                section[dependency.pretty_name] = new_version
            elif "version" in section.get(dependency.pretty_name, {}):
                section[dependency.pretty_name]["version"] = new_version


def is_pinned(version: str) -> bool:
    """Returns if `version` is an exact version."""
    return version[0].isdigit() or version.startswith("==")


def is_wildcard(version: str) -> bool:
    """Returns if `version` is a wildcard version."""
    return version[0] == "*"


def is_less_than(version: str) -> bool:
    """Returns if `version` is a less than version."""
    return version[0] == "<" and version[1].isdigit()


def is_greater_than(version: str) -> bool:
    """Returns if `version` is a greater than version."""
    return version[0] == ">" and version[1].isdigit()


def is_less_than_or_equal_to(version: str) -> bool:
    """Returns if `version` is a less than or equal to version."""
    return version.startswith("<=") and version[2].isdigit()


def is_not_equal(version: str) -> bool:
    """Returns if `version` is a not equal to version."""
    return version.startswith("!=")


def is_multiple_requirements(version: str) -> bool:
    """Returns if `version` is a multiple requirements version."""
    return len(version.split(",")) > 1


def is_bumping_prevented(dependency: Dependency, exclude: list[str]) -> bool:
    """Returns if `dependency` is not bumpable."""
    exclude.append("python")

    if dependency.source_type in ("git", "file", "directory"):
        return True

    return dependency.name in exclude
