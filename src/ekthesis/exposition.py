"""
Ideas and relations of a record that conforms to its schema, located through its layout.

Classes
-------
Idea
    Idea of an exposition, referenced or authored.
Relation
    Rhetorical relation asserted between two ideas.
Exposition
    The ideas and relations of one record, with whether it presents research.
"""
from collections.abc import Mapping
from dataclasses import dataclass

from .errors import ResourceError
from .layout import FieldPath, Pattern, SchemaLayout
from .resources import AUTHORED_KINDS, RELATIONS

PRESENTS_RESEARCH = "presents-research"
RELATION_SOURCE = "relation-source"
RELATION_TARGET = "relation-target"


@dataclass(frozen=True)
class Idea:
    """
    Idea of an exposition.

    Attributes
    ----------
    identifier : str
        Identifier of the idea.
    path : FieldPath
        Field path of the idea in its record.
    kind : str or None
        Declared kind of an authored idea, or `None` for a referenced idea.
    """

    identifier: str
    path: FieldPath
    kind: str | None

    @property
    def authored(self) -> bool:
        """Whether the author wrote the idea, instead of referencing a unit of a source."""
        return self.kind is not None


@dataclass(frozen=True)
class Relation:
    """Rhetorical relation `name` from the idea `source` to the idea `target`."""

    path: FieldPath
    name: str
    source: str
    target: str


@dataclass(frozen=True)
class Exposition:
    """
    The ideas and the relations of one record.

    Attributes
    ----------
    presents_research : bool
        Whether the exposition presents research.
    ideas : Mapping[str, Idea]
        Ideas by identifier; the first of two ideas sharing an identifier is kept.
    relations : tuple of Relation
        Relations in the order of the record.
    """

    presents_research: bool
    ideas: Mapping[str, Idea]
    relations: tuple[Relation, ...]

    @classmethod
    def read(cls, record: object, layout: SchemaLayout, idea_definition: str) -> "Exposition":
        """
        Read the exposition of `record`, which conforms to the schema of `layout`.

        Parameters
        ----------
        record : object
            Record parsed from YAML.
        layout : SchemaLayout
            Layout of the schema of the record.
        idea_definition : str
            Name of the definition of the ideas, among the collections of the layout.
        """
        flags = [value for _, value in layout.role(PRESENTS_RESEARCH).select(record)]
        ideas_collection = layout.collections[idea_definition]
        kind_field = _field_in(layout.registries, AUTHORED_KINDS, ideas_collection.items)
        ideas: dict[str, Idea] = {}
        for path, item in ideas_collection.items.select(record):
            identifier = _single(ideas_collection.identifier, item)
            kind = _single(kind_field, item) if kind_field is not None else None
            if isinstance(identifier, str) and identifier not in ideas:
                ideas[identifier] = Idea(identifier, path, kind if isinstance(kind, str) else None)
        return cls(
            presents_research=bool(flags and flags[0] is True),
            ideas=ideas,
            relations=tuple(_relations(record, layout)),
        )


def _relations(record: object, layout: SchemaLayout) -> list[Relation]:
    source_role, target_role = layout.role(RELATION_SOURCE), layout.role(RELATION_TARGET)
    items = Pattern(source_role.segments[:-1])
    if Pattern(target_role.segments[:-1]) != items:
        raise ResourceError("the source and the target of a relation lie in different items")
    name_field = _field_in(layout.registries, RELATIONS, items)
    if name_field is None:
        raise ResourceError("the schema declares no field of the registry of relations")
    relations = []
    for path, item in items.select(record):
        values = (
            _single(name_field, item),
            _single(Pattern(source_role.segments[-1:]), item),
            _single(Pattern(target_role.segments[-1:]), item),
        )
        name, source, target = values
        if isinstance(name, str) and isinstance(source, str) and isinstance(target, str):
            relations.append(Relation(path, name, source, target))
    return relations


def _field_in(
    annotated: tuple[tuple[Pattern, str], ...], value: str, items: Pattern
) -> Pattern | None:
    """Return the pattern, relative to `items`, of the field annotated by `value` under `items`."""
    for pattern, annotation in annotated:
        relative = pattern.relative_to(items)
        if annotation == value and relative is not None and relative.segments:
            return relative
    return None


def _single(pattern: Pattern, item: object) -> object:
    values = [value for _, value in pattern.select(item)]
    return values[0] if values else None
