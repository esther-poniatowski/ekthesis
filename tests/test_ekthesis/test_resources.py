"""Tests of the packaged schemas and registries, and of the layout read from the schema."""
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
