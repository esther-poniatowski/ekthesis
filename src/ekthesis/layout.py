"""
Roles of the fields of a record, read from the annotations of its schema.

The check names no field of a record: it reads from the schema where each role sits. The schema
declares the roles by six keywords:

- `x-identifier` at the root names the field path of the identifier of the record, as in Ekphrasis;
- `x-identifier` on a definition reached as the items of a sequence names the field holding the
  identifier of each item, so that the sequence is a collection of identified items;
- `x-refers` on a field names the definition whose items the field identifies;
- `x-registry` on a field names the registry to which its value belongs;
- `x-resolves: file` on a field marks a Markdown link to the source of an idea;
- `x-role` on a field names its role in the rules on sources: `source-bound`,
  `relation-source` or `relation-target`.

An `x-registry` declared inside a branch of a `oneOf` or an `anyOf` applies only to a node that
satisfies that branch, so that one field may follow a registry in one form of an item and not in
another. Every other annotation lies outside such branches.

Classes
-------
Pattern
    Field path of a schema node, in which each sequence item is a wildcard.
FieldPath
    Field path of one node of a record.
Collection
    Sequence of identified items.
Branch
    Branch of a `oneOf` or an `anyOf` within which an annotation lies.
RegistryField
    Field whose values belong to a registry, within the branches that declare it.
SchemaLayout
    Roles of the fields of a schema.
"""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field, replace

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]  # no stubs in the environment

from .errors import ResourceError

ITEM = "[*]"
"""Segment of a pattern standing for every item of a sequence."""

Segment = str | int


@dataclass(frozen=True)
class FieldPath:
    """Field path of one node of a record, as a sequence of keys and positions."""

    segments: tuple[Segment, ...] = ()

    def child(self, segment: Segment) -> "FieldPath":
        """Return the path of the child `segment` of this node."""
        return FieldPath((*self.segments, segment))

    def pointer(self) -> str:
        """
        Return the JSON Pointer (RFC 6901) of this node, the empty string for the root.

        Each key is escaped by writing `~` as `~0`, then `/` as `~1`; a position is written in
        decimal.

        Examples
        --------
        >>> FieldPath(("relations", 2, "target")).pointer()
        '/relations/2/target'
        >>> FieldPath(("a/b", "c~1d")).pointer()
        '/a~1b/c~01d'
        """
        return "".join(
            "/" + str(segment).replace("~", "~0").replace("/", "~1") for segment in self.segments
        )

    def __str__(self) -> str:
        text = ""
        for segment in self.segments:
            if isinstance(segment, int):
                text += f"[{segment}]"
            elif "." in segment or "[" in segment:
                text += f'["{segment}"]'
            else:
                text += f".{segment}" if text else segment
        return text


@dataclass(frozen=True)
class Pattern:
    """Field path of a schema node, whose segment `[*]` stands for every item of a sequence."""

    segments: tuple[str, ...] = ()

    def child(self, segment: str) -> "Pattern":
        """Return the pattern of the child `segment` of this node."""
        return Pattern((*self.segments, segment))

    def relative_to(self, prefix: "Pattern") -> "Pattern | None":
        """Return the rest of this pattern after `prefix`, or `None` if it does not start so."""
        size = len(prefix.segments)
        if self.segments[:size] != prefix.segments:
            return None
        return Pattern(self.segments[size:])

    def select(
        self, value: object, at: FieldPath = FieldPath()
    ) -> Iterator[tuple[FieldPath, object]]:
        """
        Yield each node of `value` that this pattern designates, with its field path.

        Parameters
        ----------
        value : object
            Node from which the pattern starts, such as a record parsed from YAML.
        at : FieldPath
            Field path of `value` in its record.

        Yields
        ------
        tuple of FieldPath and object
            Path and value of each designated node that the record holds.
        """
        if not self.segments:
            yield at, value
            return
        head, rest = self.segments[0], Pattern(self.segments[1:])
        if head == ITEM:
            if isinstance(value, list):
                for position, item in enumerate(value):
                    yield from rest.select(item, at.child(position))
        elif isinstance(value, Mapping) and head in value:
            yield from rest.select(value[head], at.child(head))

    def __str__(self) -> str:
        return ".".join(self.segments).replace(f".{ITEM}", ITEM)


@dataclass(frozen=True)
class Collection:
    """
    Sequence of identified items, such as the ideas of a record.

    Attributes
    ----------
    definition : str
        Name of the definition of its items under `$defs`.
    items : Pattern
        Pattern of its items.
    identifier : Pattern
        Pattern of the identifier of an item, relative to that item.
    """

    definition: str
    items: Pattern
    identifier: Pattern


@dataclass(frozen=True)
class Branch:
    """
    Branch of a `oneOf` or an `anyOf` within which an annotation lies.

    Attributes
    ----------
    anchor : Pattern
        Pattern of the node at which the branch is declared.
    schema : Mapping[str, object]
        The branch, with the definitions of its schema, so that its references resolve.
    """

    anchor: Pattern
    schema: Mapping[str, object]

    def admits(self, node: object) -> bool:
        """Whether `node`, a node at the anchor of the branch, satisfies the branch."""
        return bool(Draft202012Validator(self.schema).is_valid(node))

    def relative_to(self, prefix: Pattern) -> "Branch | None":
        """Return this branch with its anchor relative to `prefix`, or `None` if it lies outside."""
        anchor = self.anchor.relative_to(prefix)
        return None if anchor is None else Branch(anchor, self.schema)


@dataclass(frozen=True)
class RegistryField:
    """
    Field whose values belong to a registry.

    Attributes
    ----------
    pattern : Pattern
        Pattern of the field.
    registry : str
        Name of the registry.
    branches : tuple of Branch
        Branches within which the annotation lies, the outermost first. The annotation applies to a
        node only where each branch admits the node at its anchor; it applies everywhere when the
        tuple is empty.
    """

    pattern: Pattern
    registry: str
    branches: tuple[Branch, ...] = ()

    def relative_to(self, prefix: Pattern) -> "RegistryField | None":
        """Return this field relative to `prefix`, or `None` if it or a branch lies outside."""
        pattern = self.pattern.relative_to(prefix)
        branches = tuple(branch.relative_to(prefix) for branch in self.branches)
        if pattern is None or any(branch is None for branch in branches):
            return None
        return RegistryField(pattern, self.registry, tuple(b for b in branches if b is not None))

    def select(
        self, value: object, at: FieldPath = FieldPath()
    ) -> Iterator[tuple[FieldPath, object]]:
        """
        Yield each node of `value` that the field designates and to which its registry applies.

        Parameters
        ----------
        value : object
            Node from which the pattern of the field starts, such as a record parsed from YAML.
        at : FieldPath
            Field path of `value` in its record.
        """
        if not self.branches:
            yield from self.pattern.select(value, at)
            return
        first = self.branches[0]
        inner = replace(self, branches=self.branches[1:]).relative_to(first.anchor)
        assert inner is not None, "a branch encloses every annotation declared within it"
        for anchor_at, node in first.anchor.select(value, at):
            if first.admits(node):
                yield from inner.select(node, anchor_at)


@dataclass(frozen=True)
class SchemaLayout:
    """
    Roles of the fields of a schema, read from its annotations.

    Attributes
    ----------
    record_identifier : Pattern or None
        Pattern of the identifier of the record, from the keyword `x-identifier` at the root.
    collections : Mapping[str, Collection]
        Collections of identified items, by the name of their definition.
    references : tuple of (Pattern, str)
        Each field that identifies an item, with the definition of that item.
    registries : tuple of RegistryField
        Each field whose value belongs to a registry, with the name of the registry.
    source_links : tuple of Pattern
        Each field holding a link to the source of an idea.
    roles : Mapping[str, Pattern]
        Field of each role in the rules on sources.
    """

    record_identifier: Pattern | None
    collections: Mapping[str, Collection]
    references: tuple[tuple[Pattern, str], ...]
    registries: tuple[RegistryField, ...]
    source_links: tuple[Pattern, ...]
    roles: Mapping[str, Pattern]

    @classmethod
    def from_schema(cls, schema: Mapping[str, object]) -> "SchemaLayout":
        """Read the layout of `schema`, whose references stay inside the schema."""
        walker = _Walker(schema)
        walker.walk(schema, Pattern(), frozenset())
        root_identifier = schema.get("x-identifier")
        unknown = {target for _, target in walker.references} - walker.collections.keys()
        if unknown:
            raise ResourceError(f"x-refers names no collection: {sorted(unknown)}")
        return cls(
            record_identifier=(
                Pattern(tuple(root_identifier.split(".")))
                if isinstance(root_identifier, str)
                else None
            ),
            collections=walker.collections,
            references=tuple(walker.references),
            registries=tuple(walker.registries),
            source_links=tuple(walker.source_links),
            roles=walker.roles,
        )

    def role(self, name: str) -> Pattern:
        """Return the pattern of the role `name`, which the schema must declare."""
        try:
            return self.roles[name]
        except KeyError:
            raise ResourceError(f"the schema declares no field of role {name}") from None


@dataclass
class _Walker:
    """Visitor of the nodes of a schema, collecting the annotated fields."""

    schema: Mapping[str, object]
    collections: dict[str, Collection] = field(default_factory=dict)
    references: list[tuple[Pattern, str]] = field(default_factory=list)
    registries: list[RegistryField] = field(default_factory=list)
    source_links: list[Pattern] = field(default_factory=list)
    roles: dict[str, Pattern] = field(default_factory=dict)

    def walk(
        self,
        node: object,
        at: Pattern,
        expanding: frozenset[str],
        branches: tuple[Branch, ...] = (),
    ) -> None:
        """Collect the annotations of `node` at `at`, within `branches`, then of its subschemas."""
        if not isinstance(node, Mapping):
            return
        self._annotate(node, at, branches)
        reference = node.get("$ref")
        if isinstance(reference, str):
            name = self._definition_name(reference)
            if name not in expanding:
                self.walk(self._definition(name), at, expanding | {name}, branches)
        for keyword in ("oneOf", "anyOf"):
            for branch in node.get(keyword, []) or []:
                if isinstance(branch, Mapping):
                    scoped = Branch(at, {"$defs": self.schema.get("$defs", {}), **branch})
                    self.walk(branch, at, expanding, (*branches, scoped))
        for branch in node.get("allOf", []) or []:
            self.walk(branch, at, expanding, branches)
        properties = node.get("properties")
        if isinstance(properties, Mapping):
            for key, subschema in properties.items():
                self.walk(subschema, at.child(key), expanding, branches)
        items = node.get("items")
        if isinstance(items, Mapping):
            self._register_collection(items, at.child(ITEM))
            self.walk(items, at.child(ITEM), expanding, branches)

    def _annotate(
        self, node: Mapping[str, object], at: Pattern, branches: tuple[Branch, ...]
    ) -> None:
        """Record the annotations that `node` carries at `at`, within `branches`."""
        registry = node.get("x-registry")
        if isinstance(registry, str):
            self.registries.append(RegistryField(at, registry, branches))
        scoped = ("x-refers", "x-resolves", "x-role")
        if branches and any(keyword in node for keyword in scoped):
            raise ResourceError(f"an annotation at {at} other than x-registry lies in a branch")
        refers = node.get("x-refers")
        if isinstance(refers, str):
            self.references.append((at, refers))
        if node.get("x-resolves") == "file":
            self.source_links.append(at)
        role = node.get("x-role")
        if isinstance(role, str):
            if role in self.roles and self.roles[role] != at:
                raise ResourceError(f"two fields hold the role {role}")
            self.roles[role] = at

    def _register_collection(self, items: Mapping[str, object], at: Pattern) -> None:
        """Register `at` as a collection when its items refer to an identified definition."""
        reference = items.get("$ref")
        if not isinstance(reference, str):
            return
        name = self._definition_name(reference)
        identifier = self._definition(name).get("x-identifier")
        if isinstance(identifier, str):
            if name in self.collections:
                raise ResourceError(f"two sequences hold the items of {name}")
            self.collections[name] = Collection(name, at, Pattern(tuple(identifier.split("."))))

    @staticmethod
    def _definition_name(reference: str) -> str:
        """Name of the definition that a local `$ref` designates."""
        prefix = "#/$defs/"
        if not reference.startswith(prefix):
            raise ResourceError(f"the reference {reference} leaves the schema")
        return reference[len(prefix) :]

    def _definition(self, name: str) -> Mapping[str, object]:
        """Return the definition `name` of the schema."""
        definitions = self.schema.get("$defs", {})
        definition = definitions.get(name) if isinstance(definitions, Mapping) else None
        if not isinstance(definition, Mapping):
            raise ResourceError(f"the schema defines no {name}")
        return definition
