"""Tests of the check of audience records, on one valid run and one planted record per finding."""

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from ekthesis.audiences import AUDIENCE_CONTRACT, AUDIENCE_RULES
from ekthesis.check import SKIPPED_ON_UNKNOWN_CONTRACT, Checker
from ekthesis.cli import app
from ekthesis.findings import Severity
from ekthesis.resources import packaged_resources
from ekthesis.rules import CONTRACT_RULES

from .sarif_profile import profile_violations

FIXTURES = Path(__file__).parent / "fixtures" / "audiences"
VALID = sorted((FIXTURES / "valid").glob("*.yml"))
SKELETON = Path(__file__).parents[2] / "src" / "ekthesis" / "data" / "skeletons" / "audience.yml"
PLANTED = {
    "schema-conformance": (Severity.ERROR, ""),
    "unique-audiences": (Severity.ERROR, "identity.id"),
    "existing-audiences": (Severity.ERROR, "identity.narrows[0]"),
    "acyclic-parents": (Severity.ERROR, "identity.narrows[0]"),
    "undeclared-concepts": (Severity.WARNING, "knowledge[0].undeclared"),
}


@pytest.fixture(name="checker", scope="module")
def fixture_checker() -> Checker:
    """Checker reading the packaged schemas and registries."""
    return Checker(packaged_resources())


def write(directory: Path, name: str, identifier: str, narrows: list[str]) -> Path:
    """Write a minimal audience record of `identifier` narrowing `narrows`, and return its path."""
    path = directory / f"{name}.yml"
    record = {
        "_schema": AUDIENCE_CONTRACT,
        "identity": {
            "id": identifier,
            "label": identifier.replace("-", " "),
            "gloss": f"readers named {identifier}",
            "narrows": narrows,
        },
    }
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    return path


def test_every_audience_rule_has_a_planted_record() -> None:
    """The planted records cover the schema rule and every rule on audiences."""
    assert set(PLANTED) == {"schema-conformance"} | {rule.identifier for rule in AUDIENCE_RULES}


def test_valid_run_has_no_finding(checker: Checker) -> None:
    """The valid records, checked together, pass every rule."""
    assert checker.check(VALID) == []


@pytest.mark.parametrize("rule", sorted(PLANTED))
def test_planted_record_fails_its_rule_alone(checker: Checker, rule: str) -> None:
    """In a run with the valid records, each planted record yields findings of its own rule only."""
    planted = FIXTURES / "planted" / f"{rule}.yml"
    *valid, report = checker.reports([*VALID, planted])
    assert all(not other.findings for other in valid)
    severity, field = PLANTED[rule]
    assert [(f.rule, f.severity, str(f.field)) for f in report.findings] == [
        (rule, severity, field)
    ]


def test_record_breaking_its_schema_skips_the_audience_rules(checker: Checker) -> None:
    """A record that fails its schema skips the rules on audiences, and only those."""
    report = checker.report(FIXTURES / "planted" / "schema-conformance.yml")
    assert report.skipped == tuple(rule.identifier for rule in AUDIENCE_RULES)


def test_repeated_identifier_is_reported_on_the_later_record(checker: Checker) -> None:
    """The first record of an identifier keeps it, and the message names that record."""
    first = FIXTURES / "valid" / "neuroscientists.yml"
    [finding] = checker.check([first, FIXTURES / "planted" / "unique-audiences.yml"])
    assert finding.record.name == "unique-audiences.yml"
    assert str(first) in finding.message


def test_record_breaking_its_schema_still_declares_its_identifier(
    checker: Checker, tmp_path: Path
) -> None:
    """A parent whose record breaks its schema elsewhere still resolves the parent of its child."""
    parent = write(tmp_path, "parent", "parent-readers", [])
    record = yaml.safe_load(parent.read_text())
    record["identity"]["gloss"] = "Two sentences. Not a gloss"
    parent.write_text(yaml.safe_dump(record))
    child = write(tmp_path, "child", "child-readers", ["parent-readers"])
    parent_report, child_report = checker.reports([parent, child])
    assert {finding.rule for finding in parent_report.findings} == {"schema-conformance"}
    assert child_report.findings == ()


def test_cycle_through_two_records_is_reported_on_each(checker: Checker, tmp_path: Path) -> None:
    """Each parent on a cycle of two records is reported, and a parent off the cycle is not."""
    first = write(tmp_path, "first", "first-readers", ["second-readers"])
    second = write(tmp_path, "second", "second-readers", ["first-readers"])
    third = write(tmp_path, "third", "third-readers", ["first-readers"])
    reports = checker.reports([first, second, third])
    assert [[(f.rule, str(f.field)) for f in report.findings] for report in reports] == [
        [("acyclic-parents", "identity.narrows[0]")],
        [("acyclic-parents", "identity.narrows[0]")],
        [],
    ]


def test_unknown_confused_community_is_reported(checker: Checker, tmp_path: Path) -> None:
    """A confused community names an audience record of the run, as a parent does."""
    path = write(tmp_path, "readers", "readers", [])
    record = yaml.safe_load(path.read_text())
    record["identity"]["confusions"] = [
        {"community": "other-readers", "target_readers": "a", "non_target_readers": "b"}
    ]
    path.write_text(yaml.safe_dump(record))
    [finding] = checker.check([path])
    assert (finding.rule, str(finding.field)) == (
        "existing-audiences",
        "identity.confusions[0].community",
    )


def _with_target(path: Path, contract: str, field: str, value: object) -> str:
    """Rewrite the record at `path` under `contract`, with `value` at `field`; return its location."""
    record = yaml.safe_load(path.read_text())
    record["_schema"] = contract
    if field == "profile":
        record["identity"]["representatives"] = [
            {"name": "Nikolaus Kriegeskorte", "profile": value}
        ]
        located = "identity.representatives[0].profile"
    else:
        record["knowledge"] = [{"concept": value}]
        located = "knowledge[0].concept"
    path.write_text(yaml.safe_dump(record))
    return located


@pytest.mark.parametrize(
    ("field", "value", "valid"),
    [
        ("profile", {"id": "kriegeskorte_nikolaus"}, True),
        ("profile", {"repository": "geonexus", "id": "kriegeskorte_nikolaus"}, True),
        ("profile", "kriegeskorte_nikolaus", False),
        ("profile", {"id": "kriegeskorte_nikolaus", "unit": "career"}, False),
        (
            "concept",
            {"repository": "neural-coding-course", "id": "concept.coding.population"},
            True,
        ),
        ("concept", {"id": "concept.coding.population", "unit": "definition"}, True),
        ("concept", "population coding", False),
        ("concept", {}, False),
        ("concept", {"id": "concept.coding.population", "page": 3}, False),
    ],
)
def test_current_version_takes_targets_in_the_form_of_anagraphe(
    checker: Checker, tmp_path: Path, field: str, value: object, valid: bool
) -> None:
    """
    Under `ekthesis:audience@2`, a profile and a concept are logical targets of Anagraphe.

    A profile names a contact record, never a unit inside it; a concept names a record or a unit
    of any field.
    """
    path = write(tmp_path, "readers", "readers", [])
    located = _with_target(path, AUDIENCE_CONTRACT, field, value)
    findings = {(f.rule, str(f.field)) for f in checker.check([path])}
    assert findings == (set() if valid else {("schema-conformance", located)})


def test_finding_carries_the_position_of_its_field(checker: Checker) -> None:
    """A finding of a rule on audiences takes the line and the column of its node."""
    path = FIXTURES / "planted" / "undeclared-concepts.yml"
    [finding] = checker.check_record(path)
    lines = path.read_text().splitlines()
    line = next(number for number, text in enumerate(lines, 1) if "spectral analysis" in text)
    assert finding.position is not None
    assert finding.position.line == line


def test_command_passes_on_warnings_and_fails_on_errors() -> None:
    """The command exits with 0 on undeclared concepts alone, and with 1 on an unknown parent."""
    runner = CliRunner()
    warned = runner.invoke(
        app, ["check", *map(str, VALID), str(FIXTURES / "planted" / "undeclared-concepts.yml")]
    )
    assert warned.exit_code == 0, warned.output
    assert warned.output.splitlines()[-1] == "4 records checked: 0 errors, 1 warnings"
    failed = runner.invoke(app, ["check", str(FIXTURES / "planted" / "existing-audiences.yml")])
    assert failed.exit_code == 1, failed.output


def test_sarif_log_of_an_audience_run_conforms_to_the_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The log of a run of audience records conforms, and names each record by its identifier."""
    monkeypatch.chdir(FIXTURES)
    paths = [str(path.relative_to(FIXTURES)) for path in VALID] + [
        f"planted/{rule}.yml" for rule in sorted(PLANTED)
    ]
    result = CliRunner().invoke(app, ["check", "--format", "sarif", *paths])
    log = json.loads(result.output)
    assert profile_violations(log) == []
    names = {
        result["locations"][0]["logicalLocations"][0]["name"]
        for result in log["runs"][0]["results"]
    }
    assert "id:readers-with-an-undeclared-concept#/knowledge/0/undeclared" in names


def test_schema_declares_no_register() -> None:
    """The audience contract admits no register, which belongs to the glossaries of Onomasia."""
    schema = packaged_resources().schemas.get(AUDIENCE_CONTRACT)
    assert schema is not None
    assert "register" not in schema["properties"]
    assert schema["x-identifier"] == "identity.id"


def test_skeleton_names_the_contract_and_its_fields() -> None:
    """The skeleton binds the audience contract, and holds only fields of its schema."""
    skeleton = yaml.safe_load(SKELETON.read_text(encoding="utf-8"))
    schema = packaged_resources().schemas.get(AUDIENCE_CONTRACT)
    assert schema is not None
    assert skeleton["_schema"] == AUDIENCE_CONTRACT
    assert set(skeleton) <= set(schema["properties"])
    identity = schema["$defs"]["identity"]["properties"]
    assert set(skeleton["identity"]) == set(identity)


def test_run_finding_joins_its_record_in_a_mixed_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """In a run that also holds an exposition, a run finding keeps the resource and the region."""
    root = FIXTURES.parent
    monkeypatch.chdir(root)
    planted = "audiences/planted/existing-audiences.yml"
    paths = ["valid.yml", *(str(path.relative_to(root)) for path in VALID), planted]
    result = CliRunner().invoke(app, ["check", "--format", "sarif", *paths])
    log = json.loads(result.output)
    assert profile_violations(log) == []
    [found] = log["runs"][0]["results"]
    [location] = found["locations"]
    lines = (root / planted).read_text().splitlines()
    line = next(number for number, text in enumerate(lines, 1) if "missing-parent" in text)
    assert found["ruleId"] == "existing-audiences"
    assert location["physicalLocation"] == {
        "artifactLocation": {"uri": planted, "uriBaseId": "SRCROOT"},
        "region": {"startLine": line, "startColumn": lines[line - 1].index("missing-parent") + 1},
    }
    assert location["logicalLocations"] == [{"name": "id:orphan-readers#/identity/narrows/0"}]


def test_unknown_contract_skips_the_rules_of_every_contract(
    checker: Checker, tmp_path: Path
) -> None:
    """A record naming no known contract skips the rules on argument and on audience records."""
    path = tmp_path / "record.yml"
    path.write_text("_schema: 'ekthesis:audiense@1'\n")
    report = checker.report(path)
    assert report.skipped == SKIPPED_ON_UNKNOWN_CONTRACT
    assert set(report.skipped) == {
        rule.identifier for rules in CONTRACT_RULES.values() for rule in rules
    }
    assert {"existing-audiences", "authored-relations"} <= set(report.skipped)


@pytest.mark.parametrize(
    ("metadata", "valid"),
    [({}, True), ({"role": "spec", "anything": [1, {"nested": True}]}, True), ("spec", False)],
)
def test_metadata_is_reserved_to_the_consumer(
    checker: Checker, tmp_path: Path, metadata: object, valid: bool
) -> None:
    """The field `metadata` admits any object, whose fields the consumer fixes."""
    path = write(tmp_path, "readers", "readers", [])
    record = yaml.safe_load(path.read_text())
    record["metadata"] = metadata
    path.write_text(yaml.safe_dump(record))
    findings = [(f.rule, str(f.field)) for f in checker.check([path])]
    assert findings == ([] if valid else [("schema-conformance", "metadata")])
