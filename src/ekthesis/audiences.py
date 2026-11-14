"""
Audience records, read against the contract `ekthesis:audience@2` or its retained version
`ekthesis:audience@1`, and their checks.

An audience record describes one readership, as the decision on audiences states. A record is
checked alone for its undeclared concepts. The audience
records of one run are checked together: their identifiers are distinct, the parents and the
confused communities that they name are audience records of the run, and no chain of parents
returns to the audience from which it starts. Ekthesis does not check the membership of a
representative, which reads the contact profiles of the consumer. Until Anagraphe publishes the
form of a logical target, the schema requires only that a target is non-empty text, as Onomasia
does for `denotes`, and no rule checks its form.

Classes
-------
Audience
    The identifier of an audience record and the fields that its checks read.
RunEntry
    Audience record of a run that declares an identifier, conforming or not.

Functions
---------
read_audience(path, data) -> Audience
    Read an audience record that conforms to its schema.
load_audience(path) -> Audience
    Read the audience record at `path`, which conforms to its schema.
record_findings(audience) -> Iterator[Finding]
    Findings of one audience record checked alone.
run_findings(entries) -> dict
    Findings of the audience records of one run checked together.
closure(relation) -> dict
    Transitive closure of a relation between identifiers.

Attributes
----------
AUDIENCE_CONTRACT : str
    The current contract of an audience record.
AUDIENCE_CONTRACTS : tuple of str
    The contracts of an audience record that the check reads: the current one, and each earlier
    version retained until every record has migrated.
AUDIENCE_RULES : tuple of Rule
    The rules on audience records, beside `schema-conformance`.
"""

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml

from .findings import Finding, Rule, Severity
from .layout import FieldPath

AUDIENCE_CONTRACT = "ekthesis:audience@2"

AUDIENCE_CONTRACTS: tuple[str, ...] = (AUDIENCE_CONTRACT, "ekthesis:audience@1")

UNIQUE_AUDIENCES = Rule(
    "unique-audiences",
    "No two audience records of a run declare the same identifier.",
    Severity.ERROR,
)
EXISTING_AUDIENCES = Rule(
    "existing-audiences",
    "Every parent and every confused community that an audience names is an audience of the run.",
    Severity.ERROR,
)
ACYCLIC_PARENTS = Rule(
    "acyclic-parents",
    "No chain of parents returns to the audience from which it starts.",
    Severity.ERROR,
)
UNDECLARED_CONCEPTS = Rule(
    "undeclared-concepts",
    "A concept that an audience names under `undeclared` is stated by no source yet.",
    Severity.WARNING,
)

AUDIENCE_RULES: tuple[Rule, ...] = (
    UNIQUE_AUDIENCES,
    EXISTING_AUDIENCES,
    ACYCLIC_PARENTS,
    UNDECLARED_CONCEPTS,
)

Named = tuple[FieldPath, str]
"""A value of a record, with the field path at which the record holds it."""


@dataclass(frozen=True)
class Audience:
    """
    The identifier of an audience record and the fields that its checks read.

    Attributes
    ----------
    path : Path
        Path of the record file.
    identifier : str
        Identifier of the audience, at `identity.id`.
    parents : tuple of (FieldPath, str)
        Each parent that the audience narrows, at `identity.narrows`.
    communities : tuple of (FieldPath, str)
        Each declared community of its confusions, at `identity.confusions[].community`.
    undeclared : tuple of (FieldPath, str)
        Each undeclared concept, at `knowledge[].undeclared`.
    """

    path: Path
    identifier: str
    parents: tuple[Named, ...]
    communities: tuple[Named, ...]
    undeclared: tuple[Named, ...]


@dataclass(frozen=True)
class RunEntry:
    """
    Audience record of a run that declares an identifier.

    Attributes
    ----------
    path : Path
        Path of the record file.
    identifier : str
        Identifier that the record declares, read even when the record breaks its schema.
    audience : Audience or None
        The record read as an audience, or `None` when it breaks its schema.
    """

    path: Path
    identifier: str
    audience: Audience | None


def read_audience(path: Path, data: object) -> Audience:
    """
    Read the audience record `data`, which conforms to the schema of a contract of
    `AUDIENCE_CONTRACTS`.

    Parameters
    ----------
    path : Path
        Path of the record file.
    data : object
        Record parsed from YAML.

    Returns
    -------
    Audience
        Identifier of the audience and the fields that its checks read.
    """
    assert isinstance(data, Mapping), "a conforming audience record is a mapping"
    identity = data["identity"]
    at = FieldPath(("identity",))
    parents = tuple(
        (at.child("narrows").child(position), str(parent))
        for position, parent in enumerate(identity.get("narrows", []))
    )
    communities = tuple(
        (at.child("confusions").child(position).child("community"), str(confusion["community"]))
        for position, confusion in enumerate(identity.get("confusions", []))
        if "community" in confusion
    )
    items = list(enumerate(data.get("knowledge", [])))
    return Audience(
        path=path,
        identifier=str(identity["id"]),
        parents=parents,
        communities=communities,
        undeclared=_item_values(items, "undeclared"),
    )


def load_audience(path: Path) -> Audience:
    """Read the audience record at `path`, which conforms to its schema."""
    return read_audience(path, yaml.safe_load(path.read_text(encoding="utf-8")))


def _item_values(items: list[tuple[int, object]], key: str) -> tuple[Named, ...]:
    """Return the value of `key` in each knowledge item that holds it, with its field path."""
    return tuple(
        (FieldPath(("knowledge", position, key)), str(item[key]))
        for position, item in items
        if isinstance(item, Mapping) and key in item
    )


def _finding(rule: Rule, audience: Audience, field: FieldPath, message: str) -> Finding:
    """Build a finding of `rule` located at `field` of the record of `audience`."""
    return Finding(rule.identifier, audience.path, field, rule.severity, message)


def record_findings(audience: Audience) -> Iterator[Finding]:
    """Yield the findings of one audience record checked alone: a warning per undeclared concept."""
    for field, concept in audience.undeclared:
        yield _finding(
            UNDECLARED_CONCEPTS,
            audience,
            field,
            f"the concept {concept} is named, and stated by no source yet",
        )


def run_findings(entries: Sequence[RunEntry]) -> dict[int, list[Finding]]:
    """
    Return the findings of the audience records of one run checked together.

    Parameters
    ----------
    entries : Sequence of RunEntry
        Each audience record of the run that declares an identifier, in the order of the run,
        whether or not it conforms to its schema.

    Returns
    -------
    dict of int to list of Finding
        Findings of each entry, by its position in `entries`; an entry without a finding is
        absent. A record that breaks its schema yields no finding, but its identifier counts.
    """
    found: dict[int, list[Finding]] = {}
    first: dict[str, Path] = {}
    for position, entry in enumerate(entries):
        if entry.identifier not in first:
            first[entry.identifier] = entry.path
        elif entry.audience is not None:
            found.setdefault(position, []).append(
                _finding(
                    UNIQUE_AUDIENCES,
                    entry.audience,
                    FieldPath(("identity", "id")),
                    f"the identifier {entry.identifier} repeats that of {first[entry.identifier]}",
                )
            )
    for position, entry in enumerate(entries):
        if entry.audience is None:
            continue
        for field, name in (*entry.audience.parents, *entry.audience.communities):
            if name not in first:
                found.setdefault(position, []).append(
                    _finding(
                        EXISTING_AUDIENCES,
                        entry.audience,
                        field,
                        f"no audience record of the run has the identifier {name}",
                    )
                )
    for position, finding in _cycles(entries):
        found.setdefault(position, []).append(finding)
    return found


def _cycles(entries: Sequence[RunEntry]) -> Iterator[tuple[int, Finding]]:
    """
    Yield a finding for each parent that leads back to its child through the chain of parents.

    The relation joins each conforming audience to its parents among the conforming audiences of
    the run, the first record of a repeated identifier standing for it. A parent lies on a cycle
    when the child is the parent itself or one of its ancestors.
    """
    first: dict[str, int] = {}
    for position, entry in enumerate(entries):
        if entry.audience is not None:
            first.setdefault(entry.identifier, position)
    parents = {
        identifier: [name for _, name in _audience(entries, position).parents if name in first]
        for identifier, position in first.items()
    }
    ancestors = closure(parents)
    for identifier, position in first.items():
        audience = _audience(entries, position)
        for field, parent in audience.parents:
            if parent == identifier or identifier in ancestors.get(parent, frozenset()):
                yield position, _finding(
                    ACYCLIC_PARENTS,
                    audience,
                    field,
                    f"the parent {parent} of {identifier} leads back to {identifier} "
                    "through its parents",
                )


def _audience(entries: Sequence[RunEntry], position: int) -> Audience:
    """Return the conforming audience of the entry at `position`."""
    audience = entries[position].audience
    assert audience is not None, "only a conforming entry is read"
    return audience


def closure(relation: Mapping[str, Iterable[str]]) -> dict[str, frozenset[str]]:
    """
    Return the transitive closure of `relation`: each identifier with every identifier reachable.

    Parameters
    ----------
    relation : Mapping of str to Iterable of str
        Identifiers related to each identifier, such as the parents of each audience.

    Returns
    -------
    dict of str to frozenset of str
        The identifiers reached from each key of `relation` in one or more steps; an identifier
        lies in its own closure only when a cycle returns to it.

    Examples
    --------
    >>> closure({"a": ["b"], "b": ["c"], "c": []}) == {
    ...     "a": frozenset({"b", "c"}), "b": frozenset({"c"}), "c": frozenset()
    ... }
    True
    """
    reached: dict[str, frozenset[str]] = {}
    for start in relation:
        seen: set[str] = set()
        pending = list(relation[start])
        while pending:
            current = pending.pop()
            if current not in seen:
                seen.add(current)
                pending.extend(relation.get(current, ()))
        reached[start] = frozenset(seen)
    return reached
