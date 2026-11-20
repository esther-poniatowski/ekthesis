"""
Run the cases of the field `sources`, published by Onomasia, against the provenance of ekthesis.

Onomasia owns the field `sources` of `onomasia:scope-table@1`, and publishes its cases in
`specs/cases/sources.yml`, read here at the commit that the configuration of Kleisis pins. A remote
case fixes the `repository` written for a remote, and a state case fixes the `dirty` written for a
state of the repository and the files read. A value case states whether the schema of Onomasia
admits a value, which the tests of Onomasia check; ekthesis validates its own tables against that
schema in the tests of the scope table.
"""

import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from ekthesis.provenance import git_sources

from .pinned import PinnedFiles

CASES_PATH = "specs/cases/sources.yml"
KINDS = ("value", "remote", "state")


@pytest.fixture(name="cases", scope="module")
def fixture_cases(pinned: PinnedFiles) -> list[dict[str, Any]]:
    """The cases of the field `sources`, at the commit of Onomasia that Kleisis pins."""
    cases: list[dict[str, Any]] = yaml.safe_load(pinned.text("onomasia", CASES_PATH))["cases"]
    return cases


def _git(root: Path, *arguments: str) -> None:
    """Run one command of Git in a test repository, with a fixed identity and no signing."""
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.org",
            "-c",
            "commit.gpgsign=false",
            *arguments,
        ],
        check=True,
        capture_output=True,
    )


def _repository(root: Path, files: list[str]) -> None:
    """Create a repository at `root` whose one commit holds `files`."""
    root.mkdir()
    _git(root, "init", "--quiet")
    for name in files:
        (root / name).write_text(f"{name}\n", encoding="utf-8")
    _git(root, "add", "--", *files)
    _git(root, "commit", "--quiet", "-m", "records")


def _apply(root: Path, state: dict[str, list[str]]) -> None:
    """Make the changes of `state` after the commit: changed, staged, untracked, ignored and
    outside files."""
    for name in state.get("modified", []) + state.get("staged", []):
        (root / name).write_text(f"{name} changed\n", encoding="utf-8")
    if state.get("staged"):
        _git(root, "add", "--", *state["staged"])
    if state.get("ignored"):
        (root / ".git" / "info" / "exclude").write_text(
            "\n".join(state["ignored"]) + "\n", encoding="utf-8"
        )
    for name in state.get("untracked", []) + state.get("ignored", []):
        (root / name).write_text(f"{name}\n", encoding="utf-8")
    for name in state.get("outside", []):
        (root.parent / name).write_text(f"{name}\n", encoding="utf-8")


def test_every_case_has_one_kind_and_each_kind_is_present(cases: list[dict[str, Any]]) -> None:
    """Each case is a value, a remote or a state case, so that no case escapes the run."""
    for case in cases:
        assert len(set(KINDS) & case.keys()) == 1, case["name"]
    assert {kind for case in cases for kind in KINDS if kind in case} == set(KINDS)


def test_remote_cases(cases: list[dict[str, Any]], tmp_path: Path) -> None:
    """The provenance writes the location of the remote without its user information, and the
    root of the repository when it has no remote."""
    for case in (case for case in cases if "remote" in case):
        root = tmp_path / case["name"]
        _repository(root, ["records.yml"])
        if case["remote"] is not None:
            _git(root, "remote", "add", "origin", case["remote"])
        (source,) = git_sources(root, [root / "records.yml"])
        expected = case["expect"]["repository"].replace("{root}", str(root))
        assert source.repository == expected, case["name"]


def test_state_cases(cases: list[dict[str, Any]], tmp_path: Path) -> None:
    """A source is dirty exactly when its commit does not hold one of the files read."""
    for case in (case for case in cases if "state" in case):
        folder = tmp_path / case["name"]
        folder.mkdir()
        root = folder / "repository"
        _repository(root, case["state"]["committed"])
        _apply(root, case["state"])
        (source,) = git_sources(root, [root / name for name in case["read"]])
        assert source.dirty is case["expect"]["dirty"], case["name"]
