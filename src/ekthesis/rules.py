"""
Rules checked on an argument record, one function per rule.

The first rule binds a record to its schema and validates it. The other rules read a record that
conforms to its schema, through the layout of that schema; each rule yields its findings.

Classes
-------
BoundRecord
    Record that conforms to its schema, with the layout and the registries that the rules read.

Functions
---------
schema_conformance(path, record, catalog)
    The record names a known contract and validates against its schema.
unique_identifiers(record)
    The items of each collection have distinct identifiers.
existing_references(record)
    Every field that identifies an item names an existing item.
registry_membership(record)
    Every value of a registry field belongs to its registry.
source_links(record)
    Every link to a source resolves to a file, and its anchor exists in that file.
authored_relations(record)
    In an exposition bound to its sources, every relation with an authored idea is admitted.
relation_requirements(record)
    A relation between two referenced ideas that requires a recorded relation is unverified.

Attributes
----------
RULES : tuple of Rule
    Every rule of the check, with its summary and the severity of its findings.
RECORD_RULES : tuple of callables
    The rules applied to a record that conforms to its schema, in order.
"""

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError  # type: ignore[import-untyped]  # no stubs in the environment

from .errors import ResourceError
from .exposition import RELATION_SOURCE, Exposition, Idea
from .findings import Finding, Rule, Severity
from .layout import FieldPath, SchemaLayout
from .links import resolve_link
from .resources import BINDING_FIELD, RelationKind, Registries, RhetoricalRelation, SchemaCatalog

SCHEMA_CONFORMANCE = Rule(
    "schema-conformance",
    "The record names a known contract and validates against its schema.",
    Severity.ERROR,
)
UNIQUE_IDENTIFIERS = Rule(
    "unique-identifiers",
    "The items of each collection have distinct identifiers.",
    Severity.ERROR,
)
EXISTING_REFERENCES = Rule(
    "existing-references",
    "Every field that identifies an item names an existing item.",
    Severity.ERROR,
)
REGISTRY_MEMBERSHIP = Rule(
    "registry-membership",
    "Every value of a registry field belongs to its registry.",
    Severity.ERROR,
)
SOURCE_LINKS = Rule(
    "source-links",
    "Every link to a source resolves to a file, and its anchor exists in that file.",
    Severity.ERROR,
)
AUTHORED_RELATIONS = Rule(
    "authored-relations",
    "In an exposition bound to its sources, every relation with an authored idea is admitted.",
    Severity.ERROR,
)
RELATION_REQUIREMENTS = Rule(
    "relation-requirements",
    "A relation between two referenced ideas that requires a recorded relation is unverified.",
    Severity.WARNING,
)


@dataclass(frozen=True)
class BoundRecord:
    """
    Record that conforms to its schema.

    Attributes
    ----------
    path : Path
        Path of the record file.
    data : object
        Record parsed from YAML.
    layout : SchemaLayout
        Layout of the schema of the record.
    registries : Registries
        Registries against which the record is checked.
    """

    path: Path
    data: object
    layout: SchemaLayout
    registries: Registries

    def finding(self, rule: Rule, field: FieldPath, message: str) -> Finding:
        """Build a finding of `rule` located at `field` of this record."""
        return Finding(rule.identifier, self.path, field, rule.severity, message)

    def idea_definition(self) -> str:
        """Name of the definition of the ideas: the definition that a relation source identifies."""
        source = self.layout.role(RELATION_SOURCE)
        for pattern, definition in self.layout.references:
            if pattern == source:
                return definition
        raise ResourceError("the source of a relation identifies no collection")

    def exposition(self) -> Exposition:
        """Read the ideas and the relations of the record."""
        return Exposition.read(self.data, self.layout, self.idea_definition())


def schema_conformance(path: Path, record: object, catalog: SchemaCatalog) -> Iterator[Finding]:
    """
    Yield a finding when `record` names no known contract, or breaks the schema of its contract.

    Parameters
    ----------
    path : Path
        Path of the record file.
    record : object
        Record parsed from YAML.
    catalog : SchemaCatalog
        Schemas indexed by contract identifier.
    """
    rule = SCHEMA_CONFORMANCE
    contract = record.get(BINDING_FIELD) if isinstance(record, Mapping) else None
    if not isinstance(contract, str):
        yield Finding(
            rule.identifier,
            path,
            FieldPath((BINDING_FIELD,)),
            rule.severity,
            f"the record names no contract in its field {BINDING_FIELD}",
        )
        return
    schema = catalog.get(contract)
    if schema is None:
        yield Finding(
            rule.identifier,
            path,
            FieldPath((BINDING_FIELD,)),
            rule.severity,
            f"no schema of ekthesis binds the contract {contract}",
        )
        return
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(record), key=lambda error: list(error.path)):
        yield Finding(
            rule.identifier,
            path,
            FieldPath(tuple(error.path)),
            rule.severity,
            error.message,
            _offending_keyword(error),
        )


def _offending_keyword(error: ValidationError) -> str:
    """
    Name what a validation error rejects, apart from the other errors at its field.

    The name is the keyword that failed, followed for `required` by the missing property, since
    that keyword yields one error per missing property. The message is not used whole, since its
    wording belongs to the validator and may change between its versions.
    """
    keyword = str(error.validator)
    required = error.validator_value
    if keyword == "required" and isinstance(error.instance, Mapping) and isinstance(required, list):
        missing = (
            name
            for name in required
            if name not in error.instance and error.message.startswith(f"{name!r} ")
        )
        name = next(missing, None)
        if name is not None:
            return f"{keyword}:{name}"
    return keyword


def unique_identifiers(record: BoundRecord) -> Iterator[Finding]:
    """Yield a finding for each item whose identifier repeats an earlier item of its collection."""
    for collection in record.layout.collections.values():
        first: dict[object, FieldPath] = {}
        for path, item in collection.items.select(record.data):
            for _, identifier in collection.identifier.select(item):
                if identifier in first:
                    yield record.finding(
                        UNIQUE_IDENTIFIERS,
                        path,
                        f"the identifier {identifier} repeats that of {first[identifier]}",
                    )
                else:
                    first[identifier] = path


def existing_references(record: BoundRecord) -> Iterator[Finding]:
    """Yield a finding for each field that identifies no existing item of its collection."""
    for pattern, definition in record.layout.references:
        collection = record.layout.collections[definition]
        existing = {
            identifier
            for _, item in collection.items.select(record.data)
            for _, identifier in collection.identifier.select(item)
        }
        for path, value in pattern.select(record.data):
            if value not in existing:
                yield record.finding(
                    EXISTING_REFERENCES,
                    path,
                    f"no item of {collection.items} has the identifier {value}",
                )


def registry_membership(record: BoundRecord) -> Iterator[Finding]:
    """Yield a finding for each value of a registry field that its registry does not hold."""
    for pattern, registry in record.layout.registries:
        admitted = record.registries.identifiers(registry)
        if admitted is None:
            raise ResourceError(f"the schema names the unknown registry {registry}")
        for path, value in pattern.select(record.data):
            if value not in admitted:
                yield record.finding(
                    REGISTRY_MEMBERSHIP,
                    path,
                    f"{value} belongs to no entry of the registry {registry}",
                )


def source_links(record: BoundRecord) -> Iterator[Finding]:
    """Yield a finding for each link to a source that names no file, or an absent anchor."""
    for pattern in record.layout.source_links:
        for path, value in pattern.select(record.data):
            reason = resolve_link(str(value), record.path.parent)
            if reason is not None:
                yield record.finding(SOURCE_LINKS, path, reason)


def authored_relations(record: BoundRecord) -> Iterator[Finding]:
    """
    Yield a finding for each relation with an authored idea outside the two admitted forms.

    The rule applies to an exposition bound to its sources. A relation with an authored idea is
    admitted when it is a presentational relation that requires no recorded relation, or when its
    source is an authored idea of a kind that the relation admits and its target is referenced.
    """
    exposition = record.exposition()
    if not exposition.source_bound:
        return
    for relation in exposition.relations:
        source, target = exposition.ideas.get(relation.source), exposition.ideas.get(
            relation.target
        )
        entry = record.registries.relations.get(relation.name)
        if source is None or target is None or entry is None:
            continue
        if (source.authored or target.authored) and not _admitted(entry, source, target):
            yield record.finding(
                AUTHORED_RELATIONS,
                relation.path,
                f"the relation {relation.name} from {_describe(source)} "
                f"to {_describe(target)} takes no admitted form: a presentational relation "
                "other than an evidence or an antithesis, or an authored source of a kind "
                "that the relation admits, toward a referenced idea",
            )


def relation_requirements(record: BoundRecord) -> Iterator[Finding]:
    """Yield a warning for each relation between referenced ideas that requires a recorded one."""
    exposition = record.exposition()
    for relation in exposition.relations:
        source = exposition.ideas.get(relation.source)
        target = exposition.ideas.get(relation.target)
        entry = record.registries.relations.get(relation.name)
        if source is None or target is None or entry is None or entry.requires is None:
            continue
        if not source.authored and not target.authored:
            yield record.finding(
                RELATION_REQUIREMENTS,
                relation.path,
                f"unverified: the relation {relation.name} requires a recorded {entry.requires} "
                f"from {relation.source} to {relation.target}, "
                "and no source publishes its relations yet",
            )


def _admitted(entry: RhetoricalRelation, source: Idea, target: Idea) -> bool:
    """Whether a relation with an authored idea takes one of the admitted forms."""
    if entry.kind is RelationKind.PRESENTATIONAL and entry.requires is None:
        return True
    return (
        source.authored and not target.authored and source.kind in entry.admitted_authored_sources
    )


def _describe(idea: Idea) -> str:
    """Name `idea` with its provenance, for a message."""
    return (
        f"the authored {idea.kind} {idea.identifier}"
        if idea.authored
        else f"the referenced idea {idea.identifier}"
    )


RULES: tuple[Rule, ...] = (
    SCHEMA_CONFORMANCE,
    UNIQUE_IDENTIFIERS,
    EXISTING_REFERENCES,
    REGISTRY_MEMBERSHIP,
    SOURCE_LINKS,
    AUTHORED_RELATIONS,
    RELATION_REQUIREMENTS,
)

RECORD_RULES: tuple[Callable[[BoundRecord], Iterator[Finding]], ...] = (
    unique_identifiers,
    existing_references,
    registry_membership,
    source_links,
    authored_relations,
    relation_requirements,
)
