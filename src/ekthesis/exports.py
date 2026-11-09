"""
Exports of sources, read against the contract `ekthesis:export@1`.

An export lists the units of a source and the relations between them, each relation mapped onto a
class of the contract, as the decision on the contract of a research export states. The check reads
the exports that an exposition names, and verifies against them each relation that the exposition
presents between two ideas naming units.

Classes
-------
RecordedRelation
    Relation of an export, with its class and its ends.
Export
    The units and the relations of one export.

Functions
---------
read_export(path, schema)
    Read the export at `path`, or explain why it breaks its contract.
published_classes(schema)
    The classes that the contract admits for a relation.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]  # no stubs in the environment

#: The contract that an export follows.
EXPORT_CONTRACT = "ekthesis:export@1"


@dataclass(frozen=True)
class RecordedRelation:
    """
    Relation of an export.

    Attributes
    ----------
    relation_class : str
        Class of the contract onto which the source maps the relation.
    source, target : str
        Ends of a binary relation, empty for a set relation.
    members : frozenset of str
        Members of a set relation, empty for a binary relation.
    symmetric : bool
        Whether the relation holds in both directions.
    """

    relation_class: str
    source: str
    target: str
    members: frozenset[str]
    symmetric: bool

    def joins(self, source: str, target: str) -> bool:
        """
        Whether the relation holds from `source` to `target`.

        A set relation joins two units only when its members are exactly these two, since a
        minimal set of more members holds of none of its pairs.

        Examples
        --------
        >>> contrast = RecordedRelation("contrast", "a.b.x", "a.b.y", frozenset(), True)
        >>> contrast.joins("a.b.y", "a.b.x")
        True
        >>> RecordedRelation("incompatibility", "", "", frozenset({"a.b.x", "a.b.y", "a.b.z"}),
        ...                  True).joins("a.b.x", "a.b.y")
        False
        """
        if self.members:
            return self.members == frozenset({source, target})
        if (self.source, self.target) == (source, target):
            return True
        return self.symmetric and (self.target, self.source) == (source, target)


@dataclass(frozen=True)
class Export:
    """
    The units and the relations of one export.

    Attributes
    ----------
    path : Path
        Path of the export file.
    units : frozenset of str
        Identifiers of the units of the export.
    relations : tuple of RecordedRelation
        Relations of the export.
    """

    path: Path
    units: frozenset[str]
    relations: tuple[RecordedRelation, ...]


def published_classes(schema: Mapping[str, object]) -> frozenset[str]:
    """Return the classes that the contract admits for a relation, from its own enumeration."""
    definitions = schema.get("$defs")
    relation = definitions.get("relation") if isinstance(definitions, Mapping) else None
    properties = relation.get("properties") if isinstance(relation, Mapping) else None
    declared = properties.get("class") if isinstance(properties, Mapping) else None
    values = declared.get("enum") if isinstance(declared, Mapping) else None
    return frozenset(str(value) for value in values or [])


def read_export(path: Path, schema: Mapping[str, object]) -> tuple[Export | None, str | None]:
    """
    Read the export at `path`, or explain why it breaks its contract.

    Returns
    -------
    tuple
        The export, or `None` with the reason for which the file is no conforming export.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        return None, f"cannot read the export: {error}"
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        where = "/".join(str(segment) for segment in errors[0].path) or "the root"
        return None, f"the export breaks its contract at {where}: {errors[0].message}"
    assert isinstance(data, Mapping), "a conforming export is a mapping"
    units = frozenset(str(unit["id"]) for unit in data["units"])
    relations = tuple(
        RecordedRelation(
            str(entry["class"]),
            str(entry.get("source", "")),
            str(entry.get("target", "")),
            frozenset(str(member) for member in entry.get("members", [])),
            bool(entry.get("symmetric", False)),
        )
        for entry in data["relations"]
    )
    return Export(path, units, relations), None


def recorded(exports: Iterable[Export], relation_class: str, source: str, target: str) -> bool:
    """Whether one of `exports` records a relation of `relation_class` from `source` to `target`."""
    return any(
        relation.relation_class == relation_class and relation.joins(source, target)
        for export in exports
        for relation in export.relations
    )
