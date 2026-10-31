"""Tests of the packaged schemas and registries, and of the layout read from the schema."""
from jsonschema import Draft202012Validator

from ekthesis.layout import ITEM, Pattern, SchemaLayout
from ekthesis.resources import RelationKind, packaged_resources

RESOURCES = packaged_resources()
CONTRACT = "ekthesis:exposition@1"


def test_schema_binds_its_contract() -> None:
    """The exposition schema is indexed by the contract that it binds."""
    schema = RESOURCES.schemas.get(CONTRACT)
    assert schema is not None
    assert "_schema" in schema["required"]


def test_layout_reads_every_role_from_the_annotations() -> None:
    """The layout locates the identifiers, references, registries, links and roles."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas[CONTRACT])
    assert layout.record_identifier == Pattern(("exposition", "id"))
    assert {name: str(collection.items) for name, collection in layout.collections.items()} == {
        "idea": f"ideas{ITEM}",
        "part": f"parts{ITEM}",
    }
    assert {str(pattern) for pattern, _ in layout.references} == {
        f"relations{ITEM}.source", f"relations{ITEM}.target", f"parts{ITEM}.ideas{ITEM}",
    }
    assert {(str(pattern), name) for pattern, name in layout.registries} == {
        (f"ideas{ITEM}.kind", "authored-kinds"), (f"relations{ITEM}.relation", "relations"),
    }
    assert [str(pattern) for pattern in layout.source_links] == [f"ideas{ITEM}.source"]


def test_registries_state_the_requirements_of_the_decision() -> None:
    """Among presentational relations, only an evidence and an antithesis require a class."""
    relations = RESOURCES.registries.relations
    requiring = {
        entry.id: entry.requires
        for entry in relations.values()
        if entry.kind is RelationKind.PRESENTATIONAL and entry.requires is not None
    }
    assert requiring == {"evidence": "support", "antithesis": "incompatibility"}
    assert all(
        entry.requires is not None for entry in relations.values() if entry.kind is RelationKind.SUBJECT_MATTER
    )


def test_registry_of_authored_kinds_is_closed_at_four() -> None:
    """The authored kinds are the four of the decision."""
    assert set(RESOURCES.registries.authored_kinds) == {"illustration", "analogy", "motivation", "premise"}


def _annotated_nodes(node: object):
    """Yield every subschema of `node` that carries the keyword `examples`."""
    if isinstance(node, dict):
        if "examples" in node:
            yield node
        for value in node.values():
            yield from _annotated_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _annotated_nodes(value)


def test_every_example_of_the_schema_validates_against_its_field() -> None:
    """An example that its own field rejects would mislead the author of a record."""
    schema = RESOURCES.schemas.schemas[CONTRACT]
    nodes = list(_annotated_nodes(schema))
    assert nodes
    for node in nodes:
        validator = Draft202012Validator({"$defs": schema["$defs"], **node})
        for example in node["examples"]:
            assert not list(validator.iter_errors(example)), (node.get("title"), example)


def test_only_the_elaboration_admits_an_authored_source() -> None:
    """The second form admits an illustration; the third form admits no kind until a synthesis kind exists."""
    admitting = {
        entry.id: entry.admitted_authored_sources
        for entry in RESOURCES.registries.relations.values()
        if entry.admitted_authored_sources
    }
    assert admitting == {"elaboration": frozenset({"illustration"})}
