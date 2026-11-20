"""
Files of a dependency at the commit that the configuration of Kleisis pins.

The tests read the schema and the cases of another tool at the commit that
`config/tools/kleisis.yml` pins, so that a test and the closure that Kleisis materializes read one
state of that tool. Git fetches that commit from the repository of the dependency once per test
session. A commit that cannot be fetched fails the test that needs it, instead of skipping it.

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

import yaml
from jsonschema import Draft202012Validator
from kleisis.registry import read_registry
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

CONFIGURATION = Path(__file__).resolve().parents[2] / "config" / "tools" / "kleisis.yml"
"""Configuration of Kleisis, which pins the commit of each dependency."""


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

    @staticmethod
    def source(dependency: str) -> tuple[str, str]:
        """Return the repository and the commit at which the configuration pins `dependency`."""
        configuration = yaml.safe_load(CONFIGURATION.read_text(encoding="utf-8"))
        [entry] = [item for item in configuration["dependencies"] if item["id"] == dependency]
        return entry["source"]["repository"], entry["source"]["commit"]

    def read(self, dependency: str, path: str) -> bytes:
        """Return the bytes of the file `path` of `dependency` at its pinned commit."""
        repository, commit = self.source(dependency)
        clone = self.folder / f"{dependency}.git"
        if dependency not in self._fetched:
            _git("init", "--quiet", "--bare", str(clone))
            _git("-C", str(clone), "fetch", "--quiet", "--depth", "1", repository, commit)
            self._fetched.add(dependency)
        return _git("-C", str(clone), "show", f"{commit}:{path}")

    def text(self, dependency: str, path: str) -> str:
        """Return the text of the file `path` of `dependency` at its pinned commit."""
        return self.read(dependency, path).decode("utf-8")

    def validator(self, dependency: str, contract: str) -> Draft202012Validator:
        """
        Return the validator of `contract`, a contract that `dependency` exports, at its pinned
        commit.

        The registry of the dependency, read by the reader of Kleisis, names the file of the
        contract; each relative `$ref` of that file resolves to the file beside it at the same
        commit.
        """
        configuration = yaml.safe_load(CONFIGURATION.read_text(encoding="utf-8"))
        [entry] = [item for item in configuration["dependencies"] if item["id"] == dependency]
        with tempfile.TemporaryDirectory() as folder:
            registry_path = Path(folder) / "schema-registry.yml"
            registry_path.write_bytes(self.read(dependency, entry["registry"]))
            location = str(read_registry(registry_path).schemas[contract])
        schema = yaml.safe_load(self.text(dependency, location))
        base = posixpath.dirname(location)

        def retrieve(uri: str) -> Resource:
            """Read the schema that a relative `$ref` names, beside the file of the contract."""
            text = self.text(dependency, posixpath.normpath(posixpath.join(base, uri)))
            return Resource.from_contents(yaml.safe_load(text), default_specification=DRAFT202012)

        return Draft202012Validator(schema, registry=Registry(retrieve=retrieve))
