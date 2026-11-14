"""Tests of the check of constraints records, and of the field of an exposition that names one."""

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from ekthesis.check import Checker
from ekthesis.cli import app
from ekthesis.findings import Severity
from ekthesis.resources import packaged_resources
from ekthesis.rules import CONSTRAINTS_CONTRACT, CONSTRAINTS_RULES, EXPOSITION_CONTRACT

from .sarif_profile import profile_violations

FIXTURES = Path(__file__).parent / "fixtures"
VALID = sorted((FIXTURES / "constraints" / "valid").glob("*.yml"))
SKELETON = Path(__file__).parents[2] / "src" / "ekthesis" / "data" / "skeletons" / "constraints.yml"
PLANTED = {
    "schema-conformance": "constraints[0]",
    "unique-identifiers": "constraints[1]",
    "unique-units": "constraints[0]",
    "existing-references": "constraints[1].sources[1]",
}


@pytest.fixture(name="checker", scope="module")
def fixture_checker() -> Checker:
    """Checker reading the packaged schemas and registries."""
    return Checker(packaged_resources())


def _schema(contract: str) -> Any:
    """Return the packaged schema of `contract`."""
    schema = packaged_resources().schemas.get(contract)
    assert schema is not None
    return schema


def test_every_rule_on_constraints_has_a_planted_record() -> None:
    """The planted records cover the schema rule and every rule applied to a constraints record."""
    assert set(PLANTED) == {"schema-conformance"} | {rule.identifier for rule in CONSTRAINTS_RULES}


@pytest.mark.parametrize("path", VALID, ids=[path.stem for path in VALID])
def test_record_of_each_shape_has_no_finding(checker: Checker, path: Path) -> None:
    """A record without groups, a record whose constraints all belong to groups, and a record whose
    group gathers some constraints only pass every rule, and declare their identifier."""
    report = checker.report(path)
    assert report.findings == ()
    assert report.identifier == yaml.safe_load(path.read_text(encoding="utf-8"))["identity"]["id"]


@pytest.mark.parametrize("rule", sorted(PLANTED))
def test_planted_record_fails_its_rule_alone(checker: Checker, rule: str) -> None:
    """Each planted record yields one error of its own rule, at the planted field."""
    findings = checker.check_record(FIXTURES / "constraints" / "planted" / f"{rule}.yml")
    assert [(f.rule, f.severity, str(f.field)) for f in findings] == [
        (rule, Severity.ERROR, PLANTED[rule])
    ]


@pytest.mark.parametrize(
    ("collection", "position", "located"),
    [("sources", 0, "sources[0]"), ("constraints", 2, "constraints[2]")],
)
def test_identifier_shared_across_collections_is_reported_once(
    checker: Checker, tmp_path: Path, collection: str, position: int, located: str
) -> None:
    """Groups, sources and constraints share one namespace of units: an item taking the
    identifier of a group is reported at that item, and a group keeps its identifier."""
    record = yaml.safe_load(VALID[0].read_text(encoding="utf-8"))
    record[collection][position]["id"] = record["groups"][0]["id"]
    if collection == "sources":
        for item in record["constraints"]:
            item["sources"] = [
                record["groups"][0]["id"] if s == "call" else s for s in item["sources"]
            ]
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record, allow_unicode=True), encoding="utf-8")
    findings = [(f.rule, str(f.field)) for f in checker.check_record(path)]
    assert findings == [("unique-units", located)]


def test_group_names_a_declared_group(checker: Checker, tmp_path: Path) -> None:
    """A constraint whose group the record does not declare is reported, as an unknown source is."""
    record = yaml.safe_load(VALID[0].read_text(encoding="utf-8"))
    grouped = next(item for item in record["constraints"] if "group" in item)
    grouped["group"] = "undeclared-group"
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record, allow_unicode=True), encoding="utf-8")
    position = record["constraints"].index(grouped)
    [finding] = checker.check_record(path)
    assert (finding.rule, str(finding.field)) == (
        "existing-references",
        f"constraints[{position}].group",
    )


def test_record_breaking_its_schema_skips_the_rules_on_constraints(checker: Checker) -> None:
    """A record that fails its schema skips the rules on identifiers and references."""
    report = checker.report(FIXTURES / "constraints" / "planted" / "schema-conformance.yml")
    assert report.skipped == tuple(rule.identifier for rule in CONSTRAINTS_RULES)


@pytest.mark.parametrize(
    ("location", "valid"),
    [
        ("https://pints.fr/submit.html", True),
        ({"id": "instructions_poster_2026-08_ccn"}, True),
        ({"repository": "geonexus", "id": "instructions_poster_2026-08_ccn", "unit": "size"}, True),
        ("venue/instructions_poster.md", False),
        ({"repository": "geonexus"}, False),
    ],
)
def test_location_is_a_page_or_a_record(
    checker: Checker, tmp_path: Path, location: object, valid: bool
) -> None:
    """A source is read at the address of a page, or in the record named by a logical target; a
    relative path, and a target naming a repository alone, are rejected."""
    record = yaml.safe_load(VALID[0].read_text(encoding="utf-8"))
    record["sources"][0]["location"] = location
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record, allow_unicode=True), encoding="utf-8")
    findings = {(f.rule, str(f.field)) for f in checker.check_record(path)}
    assert findings == (set() if valid else {("schema-conformance", "sources[0].location")})


def _exposition(tmp_path: Path, value: object) -> Path:
    """Write the valid argument record with `value` under `venue-constraints`; return its path."""
    text = (FIXTURES / "valid.yml").read_text(encoding="utf-8").replace("(sources/", "(../sources/")
    record = yaml.safe_load(text)
    record["exposition"]["venue-constraints"] = value
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ({"id": "constraints_submission_2026-11_pints"}, True),
        ({"repository": "geonexus", "id": "constraints_submission_2026-11_pints"}, True),
        ("[Submission constraints](https://example.org/constraints_submission.md)", True),
        ({"id": "constraints_submission_2026-11_pints", "unit": "poster-size"}, False),
        ({"repository": "geonexus"}, False),
        ("constraints_submission_2026-11_pints", False),
    ],
)
def test_exposition_names_its_constraints_by_target_or_by_link(
    checker: Checker, tmp_path: Path, value: object, valid: bool
) -> None:
    """Under `ekthesis:exposition@3`, the venue constraints are a constraints record, named by a
    logical target that names no unit, or a note of constraints, named by a link as before."""
    findings = {(f.rule, str(f.field)) for f in checker.check_record(_exposition(tmp_path, value))}
    assert findings == (
        set() if valid else {("schema-conformance", "exposition.venue-constraints")}
    )


def test_exposition_types_the_target_by_the_constraints_contract() -> None:
    """
    The target of the venue constraints declares the contract of its record for Anagraphe.

    Ekthesis resolves no target: `anagraphe targets check` reports a target whose record follows
    another contract, such as an audience record, as `target-contract-mismatch`, by this
    declaration.
    """
    field = _schema(EXPOSITION_CONTRACT)["$defs"]["exposition"]["properties"]["venue-constraints"]
    [target] = [branch for branch in field["oneOf"] if "x-target-contract" in branch]
    assert target["$ref"].endswith("addressing.v1.schema.yml#/$defs/target")
    contract = CONSTRAINTS_CONTRACT.split("@", maxsplit=1)[0]
    assert target["x-target-contract"] == [contract]
    assert _schema(CONSTRAINTS_CONTRACT)["x-identifier"] == "identity.id"


def test_skeleton_names_the_contract_and_its_fields() -> None:
    """The skeleton binds the constraints contract, and holds every field of its schema."""
    skeleton = yaml.safe_load(SKELETON.read_text(encoding="utf-8"))
    schema = _schema(CONSTRAINTS_CONTRACT)
    assert skeleton["_schema"] == CONSTRAINTS_CONTRACT
    assert set(skeleton) == set(schema["properties"])
    for collection, definition in [
        ("groups", "group"),
        ("sources", "source"),
        ("constraints", "constraint"),
    ]:
        [item] = skeleton[collection]
        assert set(item) == set(schema["$defs"][definition]["properties"]), collection
    assert set(skeleton["identity"]) == set(schema["$defs"]["identity"]["properties"])


def test_command_checks_constraints_records() -> None:
    """The command passes on the records of each shape, and fails on a planted record."""
    runner = CliRunner()
    passed = runner.invoke(app, ["check", str(FIXTURES / "constraints" / "valid")])
    assert passed.exit_code == 0, passed.output
    assert passed.output.splitlines()[-1] == f"{len(VALID)} records checked: 0 errors, 0 warnings"
    failed = runner.invoke(
        app, ["check", str(FIXTURES / "constraints" / "planted" / "existing-references.yml")]
    )
    assert failed.exit_code == 1, failed.output


def test_sarif_log_of_a_constraints_run_conforms_to_the_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The log of a run of constraints records conforms, and names each record by its identifier."""
    root = FIXTURES / "constraints"
    monkeypatch.chdir(root)
    paths = [str(path.relative_to(root)) for path in VALID] + [
        f"planted/{rule}.yml" for rule in sorted(PLANTED)
    ]
    result = CliRunner().invoke(app, ["check", "--format", "sarif", *paths])
    log = json.loads(result.output)
    assert not profile_violations(log)
    names = {
        found["locations"][0]["logicalLocations"][0]["name"] for found in log["runs"][0]["results"]
    }
    assert "id:constraints_poster_planted-references#/constraints/1/sources/1" in names
