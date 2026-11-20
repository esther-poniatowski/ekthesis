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
    assert {(str(pattern), names) for pattern, names in layout.references} == {
        (f"relations{ITEM.value}.source", ("idea",)),
        (f"relations{ITEM.value}.target", ("idea",)),
        (f"parts{ITEM.value}.ideas", ("idea",)),
    }
    assert {(str(field.pattern), field.registry) for field in layout.registries} == {
        (f"ideas{ITEM.value}.kind", "authored-kinds"),
        (f"relations{ITEM.value}.relation", "relations"),
    }


def test_layout_reads_the_references_of_a_constraints_record() -> None:
    """A field declaring `x-units` names an item of each collection that it lists."""
    layout = SchemaLayout.from_schema(RESOURCES.schemas.schemas["ekthesis:constraints@1"])
    assert {(str(pattern), names) for pattern, names in layout.references} == {
        (f"constraints{ITEM.value}.group", ("group",)),
        (f"constraints{ITEM.value}.sources", ("source",)),
    }


def _nodes(node: object) -> list[dict[str, object]]:
    """Return every mapping of a schema, depth first."""
    if isinstance(node, dict):
        return [node, *(found for value in node.values() for found in _nodes(value))]
    if isinstance(node, list):
        return [found for value in node for found in _nodes(value)]
    return []


@pytest.mark.parametrize("contract", sorted(RESOURCES.schemas.schemas))
def test_reference_to_an_item_is_declared_by_x_units_only(contract: str) -> None:
    """
    A field naming an item of its own record lists the arrays of the record under `x-units`, the
    keyword of Anagraphe, whose items declare `x-identifier`; no `$ref` names the identifier field
    of a definition, the form that `x-units` replaced.
    """
    schema = RESOURCES.schemas.schemas[contract]
    definitions = schema.get("$defs", {})
    identifier_fields = {
        f"#/$defs/{name}/properties/{definition['x-identifier']}"
        for name, definition in definitions.items()
        if isinstance(definition.get("x-identifier"), str)
    }
    nodes = _nodes(schema)
    assert not {node.get("$ref") for node in nodes} & identifier_fields
    for node in nodes:
        for entry in node.get("x-units", []):
            items = schema["properties"][entry]["items"]["$ref"]
            assert "x-identifier" in definitions[items.removeprefix("#/$defs/")], entry


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


def test_reference_to_an_identifier_field_names_no_item() -> None:
    """Only `x-units` makes a reference: a `$ref` to the identifier field of a definition reuses
    its schema, and names no item."""
    named = SchemaLayout.from_schema(_schema_with({"type": "string", "x-units": ["items"]}))
    assert [(str(pattern), names) for pattern, names in named.references] == [
        (f"refs{ITEM.value}", ("item",))
    ]
    other = SchemaLayout.from_schema(_schema_with({"$ref": "#/$defs/item/properties/id"}))
    assert other.references == ()


@pytest.mark.parametrize("units", [[], "items", ["refs"], ["items["], ["items", "refs"]])
def test_units_naming_no_collection_are_skipped(units: object) -> None:
    """A declaration of `x-units` that is no non-empty list of field paths, each naming a sequence
    of identified items, locates no collection; the check skips it, and leaves its report to
    Anagraphe."""
    layout = SchemaLayout.from_schema(_schema_with({"type": "string", "x-units": units}))
    assert layout.references == ()


def test_units_in_a_branch_are_skipped() -> None:
    """A declaration of `x-units` inside a branch applies to some nodes of its field only, so the
    check skips it, and leaves its reading to Anagraphe."""
    schema = _schema_with({"oneOf": [{"x-units": ["items"]}, {"type": "integer"}]})
    assert SchemaLayout.from_schema(schema).references == ()


@pytest.mark.parametrize("identifier", ["items[0].id", "a..b", 3])
def test_identifier_that_is_no_property_path_is_skipped(identifier: object) -> None:
    """
    An `x-identifier` that is no field path of property names declares nothing for the check,
    which leaves its report to Anagraphe.

    At the root, the record declares no identifier; on a definition, its sequence is no collection,
    so no `x-units` locates it.
    """
    schema = _schema_with({"type": "string", "x-units": ["items"]})
    schema["x-identifier"] = identifier
    schema["$defs"]["item"]["x-identifier"] = identifier  # type: ignore[index]
    layout = SchemaLayout.from_schema(schema)
    assert layout.record_identifier is None
    assert not layout.collections
    assert layout.references == ()


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
