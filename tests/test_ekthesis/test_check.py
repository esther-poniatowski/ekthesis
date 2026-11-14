"""Tests of the check of argument records, on one valid record and one planted record per rule."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from ekthesis.check import Checker
from ekthesis.cli import app
from ekthesis.findings import Finding, Severity
from ekthesis.resources import packaged_resources

from .other_contract import OTHER_CONTRACT, contract_without_rules

FIXTURES = Path(__file__).parent / "fixtures"
PLANTED = {
    "schema-conformance": Severity.ERROR,
    "unique-identifiers": Severity.ERROR,
    "existing-references": Severity.ERROR,
    "registry-membership": Severity.ERROR,
    "source-links": Severity.ERROR,
    "authored-relations": Severity.ERROR,
    "relation-requirements": Severity.WARNING,
}


@pytest.fixture(name="checker", scope="module")
def fixture_checker() -> Checker:
    """Checker reading the packaged schemas and registries."""
    return Checker(packaged_resources())


def test_valid_record_has_no_finding(checker: Checker) -> None:
    """The valid record passes every rule."""
    assert checker.check_record(FIXTURES / "valid.yml") == []


@pytest.mark.parametrize("rule", sorted(PLANTED))
def test_planted_record_fails_its_rule_alone(checker: Checker, rule: str) -> None:
    """Each planted record yields findings of its own rule only, at the severity of that rule."""
    findings = checker.check_record(FIXTURES / "planted" / f"{rule}.yml")
    assert findings, f"the planted record of {rule} yields no finding"
    assert {finding.rule for finding in findings} == {rule}
    assert {finding.severity for finding in findings} == {PLANTED[rule]}


@pytest.mark.parametrize(
    ("rule", "field"),
    [
        ("unique-identifiers", "parts[1]"),
        ("existing-references", "parts[1].ideas[1]"),
        ("registry-membership", "ideas[3].kind"),
        ("source-links", "ideas[0].source"),
        ("authored-relations", "relations[0]"),
        ("relation-requirements", "relations[2]"),
    ],
)
def test_finding_locates_the_planted_field(checker: Checker, rule: str, field: str) -> None:
    """Each finding names the field path of the planted defect."""
    findings = checker.check_record(FIXTURES / "planted" / f"{rule}.yml")
    assert [str(finding.field) for finding in findings] == [field]


def _planted(name: str) -> dict[str, Any]:
    """Return the planted record of the rule `name`, parsed from YAML."""
    record: dict[str, Any] = yaml.safe_load((FIXTURES / "planted" / f"{name}.yml").read_text())
    return record


def _check(checker: Checker, record: dict[str, Any], tmp_path: Path) -> list[Finding]:
    """Check `record`, written into the folder of the planted records so that its links resolve."""
    path = tmp_path / "planted" / "record.yml"
    path.parent.mkdir(exist_ok=True)
    (tmp_path / "sources").mkdir(exist_ok=True)
    (tmp_path / "sources" / "note.md").write_text((FIXTURES / "sources" / "note.md").read_text())
    path.write_text(yaml.safe_dump(record, sort_keys=False))
    return checker.check_record(path)


def test_kind_of_a_referenced_idea_lies_outside_the_registry_of_authored_kinds(
    checker: Checker, tmp_path: Path
) -> None:
    """The registry of authored kinds binds an authored idea only, so a referenced idea states the
    kind of its unit freely, and an authored idea of that kind still fails the registry."""
    record = _planted("registry-membership")
    record["ideas"][3]["kind"] = "motivation"
    assert record["ideas"][0]["kind"] not in packaged_resources().registries.authored_kinds
    assert not _check(checker, record, tmp_path)
    record["ideas"][3]["kind"] = record["ideas"][0]["kind"]
    [finding] = _check(checker, record, tmp_path)
    assert (finding.rule, str(finding.field)) == ("registry-membership", "ideas[3].kind")


def test_referenced_idea_with_an_authored_kind_stays_referenced(
    checker: Checker, tmp_path: Path
) -> None:
    """A referenced idea is told from an authored one by its source, whatever kind it states."""
    record = _planted("relation-requirements")
    record["ideas"][0]["kind"] = "illustration"
    record["relations"][2]["relation"] = "elaboration"
    findings = _check(checker, record, tmp_path)
    assert [(finding.rule, str(finding.field)) for finding in findings] == [
        ("relation-requirements", "relations[2]")
    ]
    assert "the referenced illustration mixture-input" in findings[0].message


@pytest.mark.parametrize(
    ("field", "value", "locus"),
    [
        ("kind", None, "ideas[0]"),
        ("unit", "ans.mixture.gain-shift", "ideas[0]"),
    ],
)
def test_referenced_idea_states_its_kind_and_names_no_unit(
    checker: Checker, tmp_path: Path, field: str, value: str | None, locus: str
) -> None:
    """The contract ekthesis:exposition@3 requires the kind of a referenced idea, and drops the
    unit of an export."""
    record = _valid()
    if value is None:
        del record["ideas"][0][field]
    else:
        record["ideas"][0][field] = value
    findings = _check(checker, record, tmp_path)
    assert {finding.rule for finding in findings} == {"schema-conformance"}
    assert {str(finding.field) for finding in findings} == {locus}


def test_record_names_no_export(checker: Checker, tmp_path: Path) -> None:
    """The contract ekthesis:exposition@3 drops the exports of a record."""
    record = _valid()
    record["exposition"]["exports"] = ["[Export of the project](../exports/mixture.yml)"]
    [finding] = _check(checker, record, tmp_path)
    assert (finding.rule, str(finding.field)) == ("schema-conformance", "exposition")


def test_retained_version_is_checked_by_the_rules_of_an_argument_record(checker: Checker) -> None:
    """A record of ekthesis:exposition@1 is checked until it migrates: an idea naming a unit, and a
    referenced idea stating no kind, are referenced, and a relation between them is unverified."""
    findings = checker.check_record(FIXTURES / "retained" / "exposition-v1.yml")
    assert [(finding.rule, str(finding.field)) for finding in findings] == [
        ("relation-requirements", "relations[2]")
    ]
    assert findings[0].severity is Severity.WARNING


def _valid() -> dict[str, Any]:
    """Return the valid record, with its links rewritten from the folder of the planted records."""
    text = (FIXTURES / "valid.yml").read_text().replace("(sources/", "(../sources/")
    record: dict[str, Any] = yaml.safe_load(text)
    return record


def test_record_not_bound_to_sources_admits_any_relation_with_an_authored_idea(
    checker: Checker, tmp_path: Path
) -> None:
    """The admitted forms bind only an exposition bound to its sources."""
    record = yaml.safe_load((FIXTURES / "planted" / "authored-relations.yml").read_text())
    record["exposition"]["source-bound"] = False
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record))
    findings = checker.check_record(path)
    assert "authored-relations" not in {finding.rule for finding in findings}


def test_unknown_contract_is_reported(checker: Checker, tmp_path: Path) -> None:
    """A record naming an unknown contract fails the schema rule at its binding field."""
    path = tmp_path / "record.yml"
    path.write_text("_schema: 'ekthesis:unknown@1'\n")
    [finding] = checker.check_record(path)
    assert (finding.rule, str(finding.field)) == ("schema-conformance", "_schema")


def test_record_of_a_contract_without_rules_is_checked_against_its_schema(
    tmp_path: Path,
) -> None:
    """A contract that no rule reads binds its records to its schema alone."""
    checker = Checker(contract_without_rules(tmp_path))
    path = tmp_path / "record.yml"
    path.write_text(f"_schema: '{OTHER_CONTRACT}'\n")
    assert checker.check_record(path) == []
    path.write_text(f"_schema: '{OTHER_CONTRACT}'\nvalue: 1\n")
    [finding] = checker.check_record(path)
    assert finding.rule == "schema-conformance"


def test_unreadable_record_is_reported(checker: Checker, tmp_path: Path) -> None:
    """A record that is no YAML fails the schema rule on the whole record."""
    path = tmp_path / "record.yml"
    path.write_text("ideas: [unclosed\n")
    [finding] = checker.check_record(path)
    assert (finding.rule, str(finding.field)) == ("schema-conformance", "")


@pytest.mark.parametrize(
    ("name", "code"),
    [("valid.yml", 0), ("planted/relation-requirements.yml", 0), ("planted/source-links.yml", 1)],
)
def test_command_exits_non_zero_on_a_blocking_finding(name: str, code: int) -> None:
    """The command fails on an error, and passes on a warning alone."""
    result = CliRunner().invoke(app, ["check", str(FIXTURES / name)])
    assert result.exit_code == code, result.output
