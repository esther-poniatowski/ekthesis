"""Tests of the SARIF output of the check, against the findings profile of Elenchos."""

import copy
import json
import os
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from ekthesis.cli import app
from ekthesis.layout import FieldPath
from ekthesis.rules import RULES

from .sarif_profile import profile_violations

FIXTURES = Path(__file__).parent / "fixtures"
RECORDS = [
    "valid.yml",
    *sorted(f"planted/{path.name}" for path in (FIXTURES / "planted").iterdir()),
]
VECTORS = Path(
    os.environ.get("ELENCHOS_VECTORS", Path(__file__).parents[3] / "elenchos" / "specs" / "vectors")
)

LINE = re.compile(r": (?P<severity>error|warning) \[(?P<rule>[^\]]+)\] ")
"""Severity and rule of a line of the text output."""

JsonObject = dict[str, object]


def run_check(*arguments: str) -> tuple[int, str]:
    """Run `ekthesis check` with `arguments`, and return its exit code and its output."""
    result = CliRunner().invoke(app, ["check", *arguments])
    return result.exit_code, result.output


def sarif(*paths: str) -> JsonObject:
    """Return the SARIF log that `ekthesis check --format sarif` writes for `paths`."""
    _, output = run_check("--format", "sarif", *paths)
    log: JsonObject = json.loads(output)
    return log


def results(log: JsonObject) -> list[JsonObject]:
    """Return the results of the single run of `log`."""
    runs: list[Any] = log["runs"]  # type: ignore[assignment]
    [run] = runs
    found: list[JsonObject] = run["results"]
    return found


def logical_name(result: JsonObject) -> str:
    """Return the name of the logical location of `result`."""
    name: str = result["locations"][0]["logicalLocations"][0]["name"]  # type: ignore[index]
    return name


def discriminator(result: JsonObject) -> str:
    """Return the discriminator of `result`, empty when it holds none."""
    partial: dict[str, str] = result.get("partialFingerprints", {})  # type: ignore[assignment]
    return partial.get("discriminator/v1", "")


@pytest.fixture(name="in_fixtures")
def fixture_in_fixtures(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run from the directory of the fixtures, the root against which paths are written."""
    monkeypatch.chdir(FIXTURES)
    return FIXTURES


# --- Conversion of field paths ---------------------------------------------------------------------


def decode_pointer(pointer: str) -> list[str]:
    """Split a JSON Pointer into its reference tokens, as RFC 6901 evaluates it."""
    return [token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:]]


@pytest.mark.parametrize(
    ("segments", "pointer"),
    [
        ((), ""),
        (("relations", 2, "target"), "/relations/2/target"),
        (("ideas", 0), "/ideas/0"),
        (("a/b",), "/a~1b"),
        (("m~n",), "/m~0n"),
        (("~1",), "/~01"),
        (("/~",), "/~1~0"),
        (("a.b", "[c]"), "/a.b/[c]"),
        (("",), "/"),
        (("0",), "/0"),
        (("⏫", "gloss"), "/⏫/gloss"),
    ],
)
def test_field_path_converts_to_pointer(segments: tuple[str | int, ...], pointer: str) -> None:
    """A field path converts to the JSON Pointer that designates the same node."""
    path = FieldPath(segments)
    assert path.pointer() == pointer
    assert decode_pointer(path.pointer()) == [str(segment) for segment in segments]


# --- Conformance to the profile --------------------------------------------------------------------


@pytest.mark.parametrize("record", RECORDS)
def test_log_of_each_record_conforms_to_the_profile(in_fixtures: Path, record: str) -> None:
    """The log of each fixture conforms, and holds one result per finding of the text output."""
    log = sarif(record)
    assert profile_violations(log) == []
    runs: list[Any] = log["runs"]  # type: ignore[assignment]
    [run] = runs
    assert run["tool"]["driver"]["name"] == "ekthesis"
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]] == [
        rule.identifier for rule in RULES
    ]
    _, text = run_check(record)
    lines = text.splitlines()[:-1]
    assert [(result["ruleId"], result["level"]) for result in results(log)] == [
        LINE.search(line).group("rule", "severity") for line in lines  # type: ignore[union-attr]
    ]


@pytest.mark.parametrize("record", RECORDS)
def test_results_of_a_log_have_distinct_identities(in_fixtures: Path, record: str) -> None:
    """No two results share their rule, logical location and discriminator."""
    found = results(sarif(record))
    keys = [(result["ruleId"], logical_name(result), discriminator(result)) for result in found]
    assert len(set(keys)) == len(keys)


@pytest.mark.parametrize("record", RECORDS)
def test_sarif_output_keeps_the_exit_code(in_fixtures: Path, record: str) -> None:
    """The exit code does not depend on the output format."""
    assert run_check("--format", "sarif", record)[0] == run_check(record)[0]


def test_text_format_is_the_default(in_fixtures: Path) -> None:
    """The option `--format text` writes the default output."""
    assert run_check("--format", "text", *RECORDS) == run_check(*RECORDS)


def test_result_maps_each_field_of_its_finding(in_fixtures: Path) -> None:
    """A finding maps onto its rule, level, message, file, region and logical location."""
    [result] = results(sarif("planted/registry-membership.yml"))
    assert result["ruleId"] == "registry-membership"
    assert result["level"] == "error"
    assert result["message"] == {
        "text": "anecdote belongs to no entry of the registry authored-kinds"
    }
    locations: list[Any] = result["locations"]  # type: ignore[assignment]
    [location] = locations
    lines = (FIXTURES / "planted" / "registry-membership.yml").read_text().splitlines()
    line = next(number for number, text in enumerate(lines, 1) if "anecdote" in text)
    assert location["physicalLocation"] == {
        "artifactLocation": {"uri": "planted/registry-membership.yml", "uriBaseId": "SRCROOT"},
        "region": {"startLine": line, "startColumn": lines[line - 1].index("anecdote") + 1},
    }
    assert logical_name(result) == "id:valid-poster#/ideas/3/kind"
    assert "partialFingerprints" not in result
    assert "suppressions" not in result


def test_column_counts_code_points(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column counts each Unicode code point before the node once."""
    text = (
        (FIXTURES / "valid.yml")
        .read_text()
        .replace(
            "  - id: scenes\n    statement: Natural scenes often combine several sources.\n"
            "    kind: motivation\n",
            '  - {id: scenes, statement: "Scènes 🌄 naturelles", kind: anecdote}\n',
        )
    )
    assert "anecdote" in text
    (tmp_path / "record.yml").write_text(text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    [result] = [
        result
        for result in results(sarif("record.yml"))
        if result["ruleId"] == "registry-membership"
    ]
    line = next(line for line in text.splitlines() if "anecdote" in line)
    region = result["locations"][0]["physicalLocation"]["region"]  # type: ignore[index]
    assert region["startColumn"] == line.index("anecdote") + 1


def test_finding_on_the_whole_record_has_no_region(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable record yields a result on the whole file, with the empty locus."""
    (tmp_path / "record.yml").write_text("ideas: [unclosed\n")
    monkeypatch.chdir(tmp_path)
    log = sarif("record.yml")
    assert profile_violations(log) == []
    [result] = results(log)
    assert "region" not in result["locations"][0]["physicalLocation"]  # type: ignore[index]
    assert logical_name(result) == "path:record.yml"


# --- Resource and discriminator --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "name"),
    [
        ("_schema: 'ekthesis:unknown@1'\n", "path:notes%231/record%25.yml#/_schema"),
        ("_schema: 'ekthesis:exposition@1'\n", "path:notes%231/record%25.yml"),
    ],
)
def test_record_without_identifier_uses_its_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, name: str
) -> None:
    """A record that declares no identifier is named by its escaped repository-relative path."""
    (tmp_path / "notes#1").mkdir()
    (tmp_path / "notes#1" / "record%.yml").write_text(text)
    monkeypatch.chdir(tmp_path)
    log = sarif("notes#1/record%.yml")
    assert profile_violations(log) == []
    names = {logical_name(result).split("#/")[0] for result in results(log)}
    assert names == {name.split("#/")[0]}
    uris = {
        result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]  # type: ignore[index]
        for result in results(log)
    }
    assert uris == {"notes%231/record%25.yml"}


def test_two_results_at_one_locus_get_distinct_discriminators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two schema errors at one field are separated by the property that each one misses."""
    record = yaml.safe_load((FIXTURES / "valid.yml").read_text())
    del record["ideas"][2]["id"], record["ideas"][2]["statement"]
    (tmp_path / "record.yml").write_text(yaml.safe_dump(record))
    monkeypatch.chdir(tmp_path)
    log = sarif("record.yml")
    assert profile_violations(log) == []
    found = [result for result in results(log) if logical_name(result).endswith("#/ideas/2")]
    assert sorted(discriminator(result) for result in found) == [
        "required:id",
        "required:statement",
    ]


def test_record_outside_the_working_directory_is_refused(in_fixtures: Path, tmp_path: Path) -> None:
    """A record outside the root has no repository-relative path, and the command refuses it."""
    (tmp_path / "record.yml").write_text((FIXTURES / "valid.yml").read_text())
    code, _ = run_check("--format", "sarif", str(tmp_path / "record.yml"))
    assert code == 2


# --- Known failures of the validator ---------------------------------------------------------------


def _drop_level(log: JsonObject) -> None:
    del results(log)[0]["level"]


def _add_suppressions(log: JsonObject) -> None:
    results(log)[0]["suppressions"] = []


def _duplicate_location(log: JsonObject) -> None:
    locations: list[object] = results(log)[0]["locations"]  # type: ignore[assignment]
    locations.append(copy.deepcopy(locations[0]))


def _break_pointer(log: JsonObject) -> None:
    logical = results(log)[0]["locations"][0]["logicalLocations"][0]  # type: ignore[index]
    logical["name"] = "id:valid-poster#/ideas~2/kind"


def _unversioned_key(log: JsonObject) -> None:
    results(log)[0]["partialFingerprints"] = {"discriminator": "x"}


def _drop_column_kind(log: JsonObject) -> None:
    del log["runs"][0]["columnKind"]  # type: ignore[index]


@pytest.mark.parametrize(
    "plant",
    [
        _drop_level,
        _add_suppressions,
        _duplicate_location,
        _break_pointer,
        _unversioned_key,
        _drop_column_kind,
    ],
)
def test_validator_rejects_a_planted_violation(
    in_fixtures: Path, plant: Callable[[JsonObject], None]
) -> None:
    """The validator fires on each planted violation of an otherwise conforming log."""
    log = sarif("planted/registry-membership.yml")
    plant(log)
    assert profile_violations(log) != []


@pytest.mark.skipif(not VECTORS.is_dir(), reason="the test vectors of Elenchos are not checked out")
def test_validator_rejects_the_rejected_vectors() -> None:
    """Each rejected vector of the profile breaks the validator."""
    vectors = json.loads((VECTORS / "rejected.json").read_text(encoding="utf-8"))
    assert vectors
    for vector in vectors:
        assert profile_violations(vector["log"]) != [], vector["case"]


@pytest.mark.skipif(not VECTORS.is_dir(), reason="the test vectors of Elenchos are not checked out")
def test_validator_accepts_the_identity_vectors() -> None:
    """Each identity vector of the profile, a conforming log, passes the validator."""
    vectors = json.loads((VECTORS / "identity.json").read_text(encoding="utf-8"))
    assert vectors
    for vector in vectors:
        assert profile_violations(vector["log"]) == [], vector["case"]
