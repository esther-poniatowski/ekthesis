"""
Files of a dependency at the commit that the configuration of Kleisis pins.

The tests read the schema and the cases of another tool at the commit that the configuration of
Kleisis pins, so that a test and the closure that Kleisis materializes read one state of that
tool. The configuration is found through Hodegos, in the places where Kleisis finds it. Git fetches that commit from the repository of the dependency once per test
session. A commit that cannot be fetched fails the test that needs it, instead of skipping it.

Functions
---------
kleisis_configuration() -> dict
    The configuration of Kleisis of the repository, found through Hodegos.

Classes
-------
PinnedFiles
    Reads the files of each dependency at its pinned commit, through one bare repository per
    dependency, and the validator of each of its contracts.
"""

import posixpath
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from hodegos import Tool, discover
from jsonschema import Draft202012Validator
from kleisis.registry import read_registry
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[2]
"""Root of the repository."""


def kleisis_configuration() -> dict[str, Any]:
    """Return the configuration of Kleisis of the repository, found through Hodegos."""
    location = discover(Tool("kleisis", ("yml",)), root=ROOT).configuration
    assert location is not None, "the repository holds no configuration of Kleisis"
    configuration: dict[str, Any] = yaml.safe_load(location.path.read_text(encoding="utf-8"))
    return configuration


def dependency(identifier: str) -> dict[str, Any]:
    """Return the entry of the dependency `identifier` in the configuration of Kleisis."""
    [entry] = [item for item in kleisis_configuration()["dependencies"] if item["id"] == identifier]
    return entry


def _git(*arguments: str) -> bytes:
    """Run one command of Git, and return its output, raising on a failure."""
    return subprocess.run(["git", *arguments], check=True, capture_output=True).stdout


@dataclass
class PinnedFiles:
    """
    Reads the files of each dependency at the commit that the configuration of Kleisis pins.

    Attributes
    ----------
    folder : Path
        Folder holding one bare repository per dependency, each with its pinned commit alone.
    """

    folder: Path
    _fetched: set[str] = field(default_factory=set, init=False, repr=False)

    def read(self, identifier: str, path: str) -> bytes:
        """Return the bytes of the file `path` of the dependency `identifier` at its pinned
        commit."""
        source = dependency(identifier)["source"]
        clone = self.folder / f"{identifier}.git"
        if identifier not in self._fetched:
            _git("init", "--quiet", "--bare", str(clone))
            _git(
                "-C",
                str(clone),
                "fetch",
                "--quiet",
                "--depth",
                "1",
                source["repository"],
                source["commit"],
            )
            self._fetched.add(identifier)
        return _git("-C", str(clone), "show", f"{source['commit']}:{path}")

    def text(self, identifier: str, path: str) -> str:
        """Return the text of the file `path` of the dependency `identifier` at its pinned
        commit."""
        return self.read(identifier, path).decode("utf-8")

    def validator(self, identifier: str, contract: str) -> Draft202012Validator:
        """
        Return the validator of `contract`, a contract that the dependency `identifier` exports,
        at its pinned commit.

        The registry of the dependency, read by the reader of Kleisis, names the file of the
        contract; each relative `$ref` of that file resolves to the file beside it at the same
        commit.
        """
        with tempfile.TemporaryDirectory() as folder:
            registry_path = Path(folder) / "schema-registry.yml"
            registry_path.write_bytes(self.read(identifier, dependency(identifier)["registry"]))
            location = str(read_registry(registry_path).schemas[contract])
        schema = yaml.safe_load(self.text(identifier, location))
        base = posixpath.dirname(location)

        def retrieve(uri: str) -> Resource:
            """Read the schema that a relative `$ref` names, beside the file of the contract."""
            text = self.text(identifier, posixpath.normpath(posixpath.join(base, uri)))
            return Resource.from_contents(yaml.safe_load(text), default_specification=DRAFT202012)

        return Draft202012Validator(schema, registry=Registry(retrieve=retrieve))
