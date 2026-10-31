"""
Schemas and registries read by the check, from the data of the package or from a given directory.

Classes
-------
SchemaCatalog
    Concrete schemas, indexed by the contract identifier that each one binds.
AuthoredKind
    Entry of the registry of authored kinds.
RelationKind
    Kind of a rhetorical relation in Rhetorical Structure Theory.
RhetoricalRelation
    Entry of the registry of rhetorical relations.
Registries
    The closed registries read by the check.
Resources
    Schemas and registries supplied together to the check.

Functions
---------
packaged_resources() -> Resources
    Load the schemas and registries shipped with the package.
"""
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files
from pathlib import Path

import yaml

from .errors import ResourceError

BINDING_FIELD = "_schema"
"""Root field by which a record names its contract, after the convention of Kleisis and Ekphrasis."""

AUTHORED_KINDS = "authored-kinds"
"""Name of the registry of authored kinds."""

RELATIONS = "relations"
"""Name of the registry of rhetorical relations."""

JsonObject = Mapping[str, object]


def _read_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ResourceError(f"cannot read {path}: {error}") from error


@dataclass(frozen=True)
class SchemaCatalog:
    """
    Concrete schemas, indexed by the contract identifier written at `properties._schema.const`.

    Attributes
    ----------
    schemas : Mapping[str, JsonObject]
        Schema of each contract identifier.
    """

    schemas: Mapping[str, JsonObject]

    @classmethod
    def from_directory(cls, directory: Path) -> "SchemaCatalog":
        """Index every file `*.schema.yaml` of `directory` that binds a contract identifier."""
        schemas: dict[str, JsonObject] = {}
        for path in sorted(directory.glob("*.schema.yaml")):
            schema = _read_yaml(path)
            if not isinstance(schema, Mapping):
                raise ResourceError(f"{path} holds no schema object")
            properties = schema.get("properties", {})
            binding = properties.get(BINDING_FIELD, {}) if isinstance(properties, Mapping) else {}
            contract = binding.get("const") if isinstance(binding, Mapping) else None
            if isinstance(contract, str):
                if contract in schemas:
                    raise ResourceError(f"two schemas of {directory} bind {contract}")
                schemas[contract] = schema
        return cls(schemas)

    def get(self, contract: str) -> JsonObject | None:
        """Return the schema of `contract`, or `None` when no schema binds it."""
        return self.schemas.get(contract)


@dataclass(frozen=True)
class AuthoredKind:
    """Kind that an authored idea may declare."""

    id: str
    title: str
    description: str


class RelationKind(StrEnum):
    """Kind of a rhetorical relation in Rhetorical Structure Theory."""

    SUBJECT_MATTER = "subject-matter"
    PRESENTATIONAL = "presentational"


@dataclass(frozen=True)
class RhetoricalRelation:
    """
    Rhetorical relation, with what it requires of a source and of an authored idea.

    Attributes
    ----------
    id : str
        Identifier of the relation.
    title : str
        Name of the relation.
    kind : RelationKind
        Kind of the relation in Rhetorical Structure Theory.
    nuclearity : str
        `mononuclear` or `multinuclear`.
    requires : str or None
        Class of the recorded relation required when both ideas are referenced, or `None`.
    admitted_authored_sources : frozenset of str
        Authored kinds admitted as source when the target is referenced, in an exposition that
        presents research.
    description : str
        Definition of the relation.
    """

    id: str
    title: str
    kind: RelationKind
    nuclearity: str
    requires: str | None
    admitted_authored_sources: frozenset[str]
    description: str


@dataclass(frozen=True)
class Registries:
    """
    The closed registries read by the check.

    Attributes
    ----------
    authored_kinds : Mapping[str, AuthoredKind]
        Entries of the registry of authored kinds, by identifier.
    relations : Mapping[str, RhetoricalRelation]
        Entries of the registry of rhetorical relations, by identifier.
    """

    authored_kinds: Mapping[str, AuthoredKind]
    relations: Mapping[str, RhetoricalRelation]

    def identifiers(self, registry: str) -> frozenset[str] | None:
        """Return the identifiers of the registry named `registry`, or `None` if it is unknown."""
        entries: Mapping[str, object] | None = {
            AUTHORED_KINDS: self.authored_kinds,
            RELATIONS: self.relations,
        }.get(registry)
        return None if entries is None else frozenset(entries)

    @classmethod
    def from_directory(cls, directory: Path) -> "Registries":
        """Load the registries `authored-kinds.yml` and `relations.yml` of `directory`."""
        kinds = {
            entry.text("id"): AuthoredKind(entry.text("id"), entry.text("title"), entry.text("description"))
            for entry in _entries(directory / f"{AUTHORED_KINDS}.yml", AUTHORED_KINDS)
        }
        relations: dict[str, RhetoricalRelation] = {}
        for entry in _entries(directory / f"{RELATIONS}.yml", RELATIONS):
            admitted = frozenset(entry.texts("admitted-authored-sources"))
            unknown = admitted - kinds.keys()
            if unknown:
                raise ResourceError(
                    f"relation {entry.text('id')} admits unknown authored kinds: {sorted(unknown)}"
                )
            try:
                kind = RelationKind(entry.text("kind"))
            except ValueError as error:
                raise ResourceError(f"relation {entry.text('id')}: {error}") from error
            relations[entry.text("id")] = RhetoricalRelation(
                id=entry.text("id"),
                title=entry.text("title"),
                kind=kind,
                nuclearity=entry.text("nuclearity"),
                requires=entry.optional_text("requires"),
                admitted_authored_sources=admitted,
                description=entry.text("description"),
            )
        return cls(kinds, relations)


@dataclass(frozen=True)
class _Entry:
    """Entry of a registry file, whose fields are read with their expected types."""

    path: Path
    fields: Mapping[object, object]

    def text(self, key: str) -> str:
        """Return the text under `key`, which the entry must hold."""
        value = self.fields.get(key)
        if not isinstance(value, str):
            raise ResourceError(f"an entry of {self.path} holds no text under {key}")
        return value

    def optional_text(self, key: str) -> str | None:
        """Return the text under `key`, or `None` when the entry leaves it null or absent."""
        return None if self.fields.get(key) is None else self.text(key)

    def texts(self, key: str) -> list[str]:
        """Return the list of texts under `key`, empty when the entry leaves it null or absent."""
        values = self.fields.get(key) or []
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ResourceError(f"an entry of {self.path} holds no list of texts under {key}")
        return values


def _entries(path: Path, name: str) -> list[_Entry]:
    document = _read_yaml(path)
    if not isinstance(document, Mapping) or document.get("registry") != name:
        raise ResourceError(f"{path} is not the registry {name}")
    entries = document.get("entries")
    if not isinstance(entries, list) or not all(isinstance(entry, Mapping) for entry in entries):
        raise ResourceError(f"{path} holds no list of entries")
    parsed = [_Entry(path, entry) for entry in entries]
    identifiers = [entry.text("id") for entry in parsed]
    if len(set(identifiers)) != len(identifiers):
        raise ResourceError(f"{path} repeats an identifier")
    return parsed


@dataclass(frozen=True)
class Resources:
    """Schemas and registries supplied together to the check."""

    schemas: SchemaCatalog
    registries: Registries


def packaged_resources() -> Resources:
    """Load the schemas and the registries shipped in `ekthesis/data`."""
    data = Path(str(files("ekthesis") / "data"))
    return Resources(
        SchemaCatalog.from_directory(data / "schemas"),
        Registries.from_directory(data / "registries"),
    )
