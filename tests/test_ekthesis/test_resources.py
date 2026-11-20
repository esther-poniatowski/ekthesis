"""Tests of the packaged schemas and registries, and of the layout read from the schema."""

from importlib.resources import files
from pathlib import Path

import pytest
import yaml
from anagraphe_read import ADDRESSING_ID, addressing_schema
from jsonschema import Draft202012Validator

from ekthesis.errors import ResourceError
from ekthesis.layout import ITEM, Pattern, SchemaLayout
from ekthesis.resources import RelationKind, packaged_resources

from .pinned import ROOT, dependency

RESOURCES = packaged_resources()
CONTRACT = "ekthesis:exposition@3"
RETAINED = "ekthesis:exposition@1"


@pytest.mark.parametrize("contract", [CONTRACT, RETAINED])
def test_schema_binds_its_contract(contract: str) -> None:
    """Each exposition schema, current or retained, is indexed by the contract that it binds."""
    schema = RESOURCES.schemas.get(contract)
    assert schema is not None
    assert "_schema" in schema["required"]


def test_layout_reads_every_role_from_the_annotations() -> None:
    """The layout locates the identifiers, references, registries and roles."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas[CONTRACT])
    assert layout.record_identifier == Pattern(("exposition", "id"))
    assert {name: str(collection.items) for name, collection in layout.collections.items()} == {
        "idea": f"ideas{ITEM.value}",
        "part": f"parts{ITEM.value}",
    }
    assert {str(pattern) for pattern, _ in layout.references} == {
        f"relations{ITEM.value}.source",
        f"relations{ITEM.value}.target",
        f"parts{ITEM.value}.ideas{ITEM.value}",
    }
    assert {(str(field.pattern), field.registry) for field in layout.registries} == {
        (f"ideas{ITEM.value}.kind", "authored-kinds"),
        (f"relations{ITEM.value}.relation", "relations"),
    }


def test_layout_reads_the_references_of_a_constraints_record() -> None:
    """A field whose `$ref` names the identifier field of a definition names an item of it."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas["ekthesis:constraints@1"])
    assert {(str(pattern), definition) for pattern, definition in layout.references} == {
        (f"constraints{ITEM.value}.group", "group"),
        (f"constraints{ITEM.value}.sources{ITEM.value}", "source"),
    }


def _schema_with(field: dict[str, object]) -> dict[str, object]:
    """Return a schema of identified items, whose sequence `refs` holds `field` as items."""
    return {
        "properties": {
            "items": {"type": "array", "items": {"$ref": "#/$defs/item"}},
            "refs": {"type": "array", "items": field},
        },
        "$defs": {
            "item": {
                "x-identifier": "id",
                "properties": {"id": {"type": "string"}, "label": {"type": "string"}},
            }
        },
    }


def test_reference_to_another_property_of_a_definition_names_no_item() -> None:
    """Only the identifier field makes a reference: a `$ref` to another property reuses its
    schema, and names no item."""
    named = SchemaLayout.from_schema(_schema_with({"$ref": "#/$defs/item/properties/id"}))
    assert [(str(pattern), name) for pattern, name in named.references] == [
        (f"refs{ITEM.value}", "item")
    ]
    other = SchemaLayout.from_schema(_schema_with({"$ref": "#/$defs/item/properties/label"}))
    assert other.references == ()


def test_reference_in_a_branch_is_rejected() -> None:
    """A reference applies to every node of its field, so it may not lie in a branch."""
    schema = _schema_with({"oneOf": [{"$ref": "#/$defs/item/properties/id"}, {"type": "integer"}]})
    with pytest.raises(ResourceError):
        SchemaLayout.from_schema(schema)


def test_registry_of_authored_kinds_binds_the_authored_form_only() -> None:
    """The registry of authored kinds lies in the branch of an authored idea, and selects the kind
    of an authored idea, not the kind that a referenced idea states."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas[CONTRACT])
    [kinds] = [field for field in layout.registries if field.registry == "authored-kinds"]
    assert [str(branch.anchor) for branch in kinds.branches] == [f"ideas{ITEM.value}"]
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
    schema = {"oneOf": [{"properties": {"source": {"x-role": "relation-source"}}}]}
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


@pytest.mark.parametrize("contract", [CONTRACT, RETAINED, "ekthesis:constraints@1"])
def test_every_example_of_the_schema_validates_against_its_field(contract: str) -> None:
    """An example that its own field rejects would mislead the author of a record."""
    schema = RESOURCES.schemas.schemas[contract]
    nodes = list(_annotated_nodes(schema))
    assert nodes
    for node in nodes:
        validator = Draft202012Validator(
            {"$defs": schema["$defs"], **node}, registry=RESOURCES.schemas.registry()
        )
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


def _absolute_references(node: object):
    """Yield the absolute `$ref` of `node` and of its subschemas, without their fragment."""
    if isinstance(node, dict):
        reference = node.get("$ref")
        if isinstance(reference, str) and "://" in reference:
            yield reference.split("#", 1)[0]
        for value in node.values():
            yield from _absolute_references(value)
    elif isinstance(node, list):
        for value in node:
            yield from _absolute_references(value)


def test_schemas_of_other_tools_come_from_their_owner() -> None:
    """
    Each absolute `$ref` of a schema of the package resolves through the package of its owner.

    The addressing schema is read from `anagraphe-read`, and no file of the package declares an
    absolute `$id`, so the package holds no copy of a schema of another tool.
    """
    references = RESOURCES.schemas.references
    used = {
        reference
        for schema in RESOURCES.schemas.schemas.values()
        for reference in _absolute_references(schema)
    }
    assert used and used <= set(references), used - set(references)
    assert references[ADDRESSING_ID] == addressing_schema()
    data = Path(str(files("ekthesis") / "data"))
    for path in sorted(data.rglob("*.y*ml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        identifier = document.get("$id") if isinstance(document, dict) else None
        assert not (isinstance(identifier, str) and "://" in identifier), path


def test_anagraphe_read_is_pinned_at_the_commit_that_kleisis_materializes() -> None:
    """The check reads the addressing schema from `anagraphe-read`, and Kleisis materializes the
    same resource for the consumers; both pin one commit of Anagraphe, so one `$id` maps to one
    content."""
    environment = yaml.safe_load((ROOT / "environment.yml").read_text(encoding="utf-8"))
    [pip] = [item["pip"] for item in environment["dependencies"] if isinstance(item, dict)]
    [requirement] = [item for item in pip if item.startswith("anagraphe-read @ ")]
    commit = requirement.split("@")[-1].split("#")[0]
    assert commit == dependency("anagraphe")["source"]["commit"]
