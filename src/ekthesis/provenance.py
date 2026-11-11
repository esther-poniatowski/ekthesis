"""
Provenance of a generated document: the repository, the commit and the state of its records.

A document of a contract of Onomasia names the records behind it under its common field `sources`.
Each source states the location of the repository holding the root, the full identifier of its
commit, and whether the records read held uncommitted changes. When the root lies in no Git
repository, the document names no source.

Classes
-------
Source
    Repository, commit and state of the records behind a document.

Functions
---------
git_sources(root, records) -> tuple of Source
    The repository holding `root`, with the state of `records`, read through the command `git`.
public_location(url) -> str
    The location of a repository without the user information of its URL.
"""

import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

SCP_USER = re.compile(r"\A[^@/:]+@(?=[^/:]+:)")
"""User of a remote written in the form of `scp`, `user@host:path`, which has no scheme."""


@dataclass(frozen=True)
class Source:
    """
    Repository, commit and state of the records behind a document.

    Attributes
    ----------
    repository : str
        Address of the remote `origin` of the repository, without its user information, or the
        path of the root when the repository has no such remote.
    commit : str
        Full identifier of the commit checked out.
    dirty : bool
        Whether a record read held uncommitted changes, or lay outside every commit.
    """

    repository: str
    commit: str
    dirty: bool

    def to_data(self) -> dict[str, object]:
        """Return the item of the common field `sources` that describes this source."""
        return {"repository": self.repository, "commit": self.commit, "dirty": self.dirty}


def public_location(url: str) -> str:
    """
    Return the location `url` of a repository without its user information.

    A remote may carry a user and a token, as `https://user:token@host/path`, which a generated
    document must not publish.

    Examples
    --------
    >>> public_location("https://user:token@github.com/org/repo.git")
    'https://github.com/org/repo.git'
    >>> public_location("git@github.com:org/repo.git")
    'github.com:org/repo.git'
    >>> public_location("/path/to/repo")
    '/path/to/repo'
    """
    parts = urlsplit(url)
    if parts.scheme and parts.netloc:
        host = parts.netloc.rpartition("@")[2]
        return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))
    return SCP_USER.sub("", url)


def git_sources(root: Path, records: Sequence[Path]) -> tuple[Source, ...]:
    """
    Return the repository holding `root`, or no source when `root` lies in none.

    Parameters
    ----------
    root : Path
        Root of the consumer.
    records : Sequence of Path
        Records read to generate the document. The source is dirty when one of them differs from
        its committed state, is untracked or ignored, or lies outside the repository, since no
        commit then holds it; a change to another file, such as the generated document itself,
        leaves it clean.
    """

    def git(*arguments: str) -> str | None:
        """Run one command of Git on the root, and return its output, or `None` on a failure."""
        try:
            completed = subprocess.run(
                ["git", "-C", str(root), *arguments], capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return completed.stdout.strip()

    commit = git("rev-parse", "HEAD")
    if commit is None:
        return ()
    remote = git("config", "--get", "remote.origin.url")
    repository = public_location(remote) if remote else str(root)
    paths = (str(path.resolve()) for path in records)
    status = git("status", "--porcelain", "--ignored", "--", *paths)
    return (Source(repository, commit, status is None or bool(status)),)
