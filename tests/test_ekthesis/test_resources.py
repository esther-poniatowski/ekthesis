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
        f"relations{ITEM}.source",
        f"relations{ITEM}.target",
        f"parts{ITEM}.ideas{ITEM}",
    }
    assert {(str(pattern), name) for pattern, name in layout.registries} == {
        (f"ideas{ITEM}.kind", "authored-kinds"),
        (f"relations{ITEM}.relation", "relations"),
    }
    assert [str(pattern) for pattern in layout.source_links] == [f"ideas{ITEM}.source"]


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
    """The second form admits an illustration; a synthesis is no authored idea, so no other relation admits one."""
    admitting = {
        entry.identifier: entry.admitted_authored_sources
        for entry in RESOURCES.registries.relations.values()
        if entry.admitted_authored_sources
    }
    assert admitting == {"elaboration": frozenset({"illustration"})}


EXPORT = "ekthesis:export@1"


def _export() -> dict[str, object]:
    """A valid export: two answers, a law that supports one of them, and an incompatible set."""
    unit = {"unit": "", "kind": "claim", "record_kind": "answer", "statement": "", "status": ""}
    return {
        "_schema": EXPORT,
        "id": "export.mixture",
        "type": "export",
        "source": {"repository": "mixture", "tool": "gnomon"},
        "generated_by": "gnomon export",
        "findings_overridden": False,
        "units": [
            {**unit, "id": "ans.a.x", "record": "ans.a.x"},
            {**unit, "id": "ans.a.y", "record": "ans.a.y"},
            {**unit, "id": "ans.a.z", "record": "ans.a.z", "superseded_by": ["ans.a.y"]},
            {**unit, "id": "mod.a.m.law", "record": "mod.a.m", "unit": "law", "kind": "law"},
        ],
        "relations": [
            {
                "id": "ans.a.x.shape",
                "class": "support",
                "source": "mod.a.m.law",
                "target": "ans.a.x",
                "relation": "grounds[].record",
                "use": "warrant",
            },
            {
                "id": "incompatible-with:ans.a.x,ans.a.y,ans.a.z",
                "class": "incompatibility",
                "members": ["ans.a.x", "ans.a.y", "ans.a.z"],
                "symmetric": True,
                "relation": "incompatible-with",
            },
        ],
    }


def _export_errors(export: object) -> list[str]:
    schema = RESOURCES.schemas.schemas[EXPORT]
    return [error.message for error in Draft202012Validator(schema).iter_errors(export)]


def test_export_schema_binds_its_contract_and_admits_a_valid_export() -> None:
    """The export schema is indexed by its contract, and a valid export conforms to it."""
    assert "_schema" in RESOURCES.schemas.schemas[EXPORT]["required"]
    assert _export_errors(_export()) == []


def test_export_rejects_a_class_outside_the_contract() -> None:
    """A class that the contract does not publish cannot be read by the check."""
    export = _export()
    export["relations"][0]["class"] = "volitional-cause"  # type: ignore[index]
    assert len(_export_errors(export)) == 1


def test_export_rejects_a_set_of_one_member_and_a_relation_with_both_forms_of_ends() -> None:
    """A set relation holds of two members or more, and a relation names either a source and a
    target or its members, never both."""
    export = _export()
    export["relations"][1]["members"] = ["ans.a.x"]  # type: ignore[index]
    assert len(_export_errors(export)) == 1
    export = _export()
    export["relations"][1]["source"] = "ans.a.x"  # type: ignore[index]
    assert len(_export_errors(export)) == 1


def test_every_example_of_the_export_schema_validates_against_its_field() -> None:
    """An example that its own field rejects would mislead a reader of the contract."""
    schema = RESOURCES.schemas.schemas[EXPORT]
    for node in _annotated_nodes(schema):
        validator = Draft202012Validator({"$defs": schema["$defs"], **node})
        for example in node["examples"]:
            assert not list(validator.iter_errors(example)), (node.get("title"), example)
