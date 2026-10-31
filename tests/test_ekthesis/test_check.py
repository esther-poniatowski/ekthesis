"""Tests of the check of argument records, on one valid record and one planted record per rule."""
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from ekthesis.check import Checker
from ekthesis.cli import app
from ekthesis.findings import Severity
from ekthesis.resources import packaged_resources

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
    assert [finding.field for finding in findings] == [field]


def test_record_without_research_admits_any_relation_with_an_authored_idea(
    checker: Checker, tmp_path: Path
) -> None:
    """The admitted forms bind only an exposition that presents research."""
    record = yaml.safe_load((FIXTURES / "planted" / "authored-relations.yml").read_text())
    record["exposition"]["presents-research"] = False
    path = tmp_path / "record.yml"
    path.write_text(yaml.safe_dump(record))
    findings = checker.check_record(path)
    assert "authored-relations" not in {finding.rule for finding in findings}


def test_unknown_contract_is_reported(checker: Checker, tmp_path: Path) -> None:
    """A record naming an unknown contract fails the schema rule at its binding field."""
    path = tmp_path / "record.yml"
    path.write_text("_schema: 'ekthesis:unknown@1'\n")
    [finding] = checker.check_record(path)
    assert (finding.rule, finding.field) == ("schema-conformance", "_schema")


def test_unreadable_record_is_reported(checker: Checker, tmp_path: Path) -> None:
    """A record that is no YAML fails the schema rule on the whole record."""
    path = tmp_path / "record.yml"
    path.write_text("ideas: [unclosed\n")
    [finding] = checker.check_record(path)
    assert (finding.rule, finding.field) == ("schema-conformance", "")


@pytest.mark.parametrize(
    ("name", "code"),
    [("valid.yml", 0), ("planted/relation-requirements.yml", 0), ("planted/source-links.yml", 1)],
)
def test_command_exits_non_zero_on_a_blocking_finding(name: str, code: int) -> None:
    """The command fails on an error, and passes on a warning alone."""
    result = CliRunner().invoke(app, ["check", str(FIXTURES / name)])
    assert result.exit_code == code, result.output
