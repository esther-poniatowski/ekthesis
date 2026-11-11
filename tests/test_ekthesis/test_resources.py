"""Tests of the packaged schemas and registries, and of the layout read from the schema."""

import pytest
from jsonschema import Draft202012Validator

from ekthesis.errors import ResourceError
from ekthesis.layout import ITEM, Pattern, SchemaLayout
from ekthesis.resources import RelationKind, packaged_resources

RESOURCES = packaged_resources()
CONTRACT = "ekthesis:exposition@2"
RETAINED = "ekthesis:exposition@1"


@pytest.mark.parametrize("contract", [CONTRACT, RETAINED])
def test_schema_binds_its_contract(contract: str) -> None:
    """Each exposition schema, current or retained, is indexed by the contract that it binds."""
    schema = RESOURCES.schemas.get(contract)
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
        f"relations{ITEM}.source",
        f"relations{ITEM}.target",
        f"parts{ITEM}.ideas{ITEM}",
    }
    assert {(str(field.pattern), field.registry) for field in layout.registries} == {
        (f"ideas{ITEM}.kind", "authored-kinds"),
        (f"relations{ITEM}.relation", "relations"),
    }
    assert [str(pattern) for pattern in layout.source_links] == [f"ideas{ITEM}.source"]


def test_registry_of_authored_kinds_binds_the_authored_form_only() -> None:
    """The registry of authored kinds lies in the branch of an authored idea, and selects the kind
    of an authored idea, not the kind that a referenced idea states."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas[CONTRACT])
    [kinds] = [field for field in layout.registries if field.registry == "authored-kinds"]
    assert [str(branch.anchor) for branch in kinds.branches] == [f"ideas{ITEM}"]
    record = {
        "ideas": [
            {"id": "a", "statement": "A.", "source": "[a](a.md)", "kind": "claim"},
            {"id": "b", "statement": "B.", "kind": "illustration"},
        ]
    }
    assert [(str(path), value) for path, value in kinds.select(record)] == [
        ("ideas[1].kind", "illustration")
    ]


def test_annotation_other_than_a_registry_in_a_branch_is_rejected() -> None:
    """Only a registry is scoped to a branch; another annotation there would apply everywhere."""
    schema = {"oneOf": [{"properties": {"link": {"x-resolves": "file"}}}]}
    with pytest.raises(ResourceError):
        SchemaLayout.from_schema(schema)


def test_registries_state_the_requirements_of_the_decision() -> None:
    """Among presentational relations, only an evidence and an antithesis require a class."""
    relations = RESOURCES.registries.relations
    requiring = {
        entry.identifier: entry.requires
        for entry in relations.values()
        if entry.kind is RelationKind.PRESENTATIONAL and entry.requires is not None
    }
    assert requiring == {"evidence": "support", "antithesis": "incompatibility"}
    assert all(
        entry.requires is not None
        for entry in relations.values()
        if entry.kind is RelationKind.SUBJECT_MATTER
    )


def test_registry_of_authored_kinds_is_closed_at_four() -> None:
    """The authored kinds are the four of the decision."""
    assert set(RESOURCES.registries.authored_kinds) == {
        "illustration",
        "analogy",
        "motivation",
        "premise",
    }


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


@pytest.mark.parametrize("contract", [CONTRACT, RETAINED])
def test_every_example_of_the_schema_validates_against_its_field(contract: str) -> None:
    """An example that its own field rejects would mislead the author of a record."""
    schema = RESOURCES.schemas.schemas[contract]
    nodes = list(_annotated_nodes(schema))
    assert nodes
    for node in nodes:
        validator = Draft202012Validator({"$defs": schema["$defs"], **node})
        for example in node["examples"]:
            assert not list(validator.iter_errors(example)), (node.get("title"), example)


def test_only_the_elaboration_admits_an_authored_source() -> None:
    """The second form admits an illustration; a synthesis is no authored idea, so no other relation admits one."""
    admitting = {
        entry.identifier: entry.admitted_authored_sources
        for entry in RESOURCES.registries.relations.values()
        if entry.admitted_authored_sources
    }
    assert admitting == {"elaboration": frozenset({"illustration"})}
