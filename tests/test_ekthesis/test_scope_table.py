"""Tests of the scope table derived from audience records, and of the command `scope-table`."""

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from typer.testing import CliRunner

from ekthesis.audiences import load_audience
from ekthesis.cli import app
from ekthesis.provenance import public_location
from ekthesis.scope_table import HEADER, SCOPE_TABLE_CONTRACT, Row, ScopeTable

from .sarif_profile import profile_violations

FIXTURES = Path(__file__).parent / "fixtures" / "audiences"
VALID = sorted((FIXTURES / "valid").glob("*.yml"))
ONOMASIA_SCHEMAS = Path(
    os.environ.get(
        "ONOMASIA_SCHEMAS",
        Path(__file__).parents[3] / "onomasia" / "src" / "onomasia" / "data" / "schemas",
    )
)

DERIVED = {
    "auditory-neuroscientists": Row(("neuroscientists", "systems-neuroscientists"), ()),
    "neuroscientists": Row((), ("auditory-neuroscientists", "systems-neuroscientists")),
    "systems-neuroscientists": Row(("neuroscientists",), ("auditory-neuroscientists",)),
}
"""Rows of the valid records: a chain of three audiences, each narrowing the previous one."""


def run(*arguments: str) -> tuple[int, str]:
    """Run `ekthesis scope-table` with `arguments`, and return its exit code and its output."""
    result = CliRunner().invoke(app, ["scope-table", *arguments])
    return result.exit_code, result.output


def generate(table: Path, *extra: str, root: Path | None = None) -> tuple[int, str]:
    """Run the command on the valid records and `table`, with the folder of `table` as root."""
    base = root or table.parent
    return run(*map(str, VALID), "-t", str(table), "-r", str(base), *extra)


def test_table_holds_the_closure_of_the_parents_and_of_its_inverse() -> None:
    """Ancestors close the parents transitively, and descendants close the inverse relation."""
    table = ScopeTable.derive(load_audience(path) for path in VALID)
    assert dict(table.rows) == DERIVED
    assert list(table.rows) == sorted(DERIVED)


def test_table_does_not_depend_on_the_order_of_the_records() -> None:
    """The text of a table is the same for any order of its records."""
    forward = ScopeTable.derive(load_audience(path) for path in VALID)
    backward = ScopeTable.derive(load_audience(path) for path in reversed(VALID))
    assert forward.text(()) == backward.text(())


def test_command_writes_the_same_bytes_twice(tmp_path: Path) -> None:
    """Two runs on unchanged records write identical tables."""
    table = tmp_path / "out" / "scope-table.yml"
    assert generate(table, root=tmp_path)[0] == 0
    first = table.read_bytes()
    assert generate(table, root=tmp_path)[0] == 0
    assert table.read_bytes() == first


def test_written_table_names_no_source_outside_a_repository(tmp_path: Path) -> None:
    """A root in no Git repository yields an empty `sources`, and the contract of Onomasia."""
    table = tmp_path / "scope-table.yml"
    code, output = generate(table)
    assert code == 0, output
    data = yaml.safe_load(table.read_text())
    assert data["contract"] == SCOPE_TABLE_CONTRACT
    assert data["sources"] == []
    assert data["audiences"] == {name: row.to_data() for name, row in DERIVED.items()}


def test_written_table_validates_against_the_schema_of_onomasia(tmp_path: Path) -> None:
    """The table satisfies `onomasia:scope-table@1`, read from the schemas of Onomasia."""
    schema_path = ONOMASIA_SCHEMAS / "scope-table.schema.yml"
    common_path = ONOMASIA_SCHEMAS / "common.schema.yml"
    if not (schema_path.is_file() and common_path.is_file()):
        pytest.skip(f"the schemas of Onomasia are absent from {ONOMASIA_SCHEMAS}")
    table = tmp_path / "scope-table.yml"
    generate(table)
    common = yaml.safe_load(common_path.read_text(encoding="utf-8"))
    registry: Registry = Registry().with_resource(
        "common.schema.yml", Resource.from_contents(common, default_specification=DRAFT202012)
    )
    validator = Draft202012Validator(
        yaml.safe_load(schema_path.read_text(encoding="utf-8")), registry=registry
    )
    data = yaml.safe_load(table.read_text())
    data["sources"] = [{"repository": "/a/root", "commit": "0" * 40, "dirty": True}]
    assert list(validator.iter_errors(data)) == []
    data["audiences"]["neuroscientists"]["ancestors"] = ["Not An Id"]
    assert list(validator.iter_errors(data)), "the schema rejects a planted defect"


def test_check_passes_on_a_fresh_table_and_writes_nothing(tmp_path: Path) -> None:
    """The option `--check` passes on the table just written, and leaves it unchanged."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    written = table.read_bytes()
    code, output = generate(table, "--check")
    assert code == 0, output
    assert output.splitlines()[-1] == f"{table}: current, 3 audiences derived"
    assert table.read_bytes() == written


def test_check_ignores_the_sources(tmp_path: Path) -> None:
    """A table whose sources name another commit is current, since a commit changes them."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    data = yaml.safe_load(table.read_text())
    data["sources"] = [{"repository": "/elsewhere", "commit": "1" * 40, "dirty": False}]
    table.write_text(yaml.safe_dump(data, sort_keys=False))
    assert generate(table, "--check")[0] == 0


@pytest.mark.parametrize(
    ("edit", "field"),
    [
        (lambda rows: rows["neuroscientists"]["descendants"].pop(), "audiences.neuroscientists"),
        (lambda rows: rows.pop("neuroscientists"), "audiences"),
        (
            lambda rows: rows.update({"extra-readers": {"ancestors": [], "descendants": []}}),
            "audiences.extra-readers",
        ),
    ],
    ids=["changed-row", "missing-row", "extra-row"],
)
def test_check_reports_a_stale_table(tmp_path: Path, edit: object, field: str) -> None:
    """A table that differs from the derived one fails, with one finding at the differing row."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    data = yaml.safe_load(table.read_text())
    edit(data["audiences"])  # type: ignore[operator]
    table.write_text(yaml.safe_dump(data, sort_keys=False))
    written = table.read_bytes()
    code, output = generate(table, "--check")
    assert code == 1, output
    [line, summary] = output.splitlines()
    assert line.startswith(f"{table}:{field}: error [scope-table-current] ")
    assert summary == f"{table}: 1 differences, 3 audiences derived"
    assert table.read_bytes() == written


def test_check_reports_a_missing_table(tmp_path: Path) -> None:
    """A table that does not exist is stale."""
    code, output = generate(tmp_path / "scope-table.yml", "--check")
    assert code == 1
    assert "[scope-table-current] the scope table does not exist" in output


def test_stale_table_in_sarif_conforms_to_the_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The finding on a stale table is one result of a log in the findings profile."""
    for path in VALID:
        (tmp_path / path.name).write_text(path.read_text())
    (tmp_path / "scope-table.yml").write_text(
        f"contract: {SCOPE_TABLE_CONTRACT}\nsources: []\naudiences: {{}}\n"
    )
    monkeypatch.chdir(tmp_path)
    names = [path.name for path in VALID]
    code, output = run(*names, "-t", "scope-table.yml", "--check", "--format", "sarif")
    assert code == 1
    log = json.loads(output)
    assert profile_violations(log) == []
    results = log["runs"][0]["results"]
    assert {result["ruleId"] for result in results} == {"scope-table-current"}
    assert len(results) == len(DERIVED)


@pytest.mark.parametrize("mode", [[], ["--check"]], ids=["write", "check"])
def test_errors_of_the_records_are_counted_and_not_repeated(
    tmp_path: Path, mode: list[str]
) -> None:
    """Records with errors yield one finding at the table naming their count, and no table."""
    table = tmp_path / "scope-table.yml"
    if mode:
        table.write_text("kept: true\n")
    orphan = yaml.safe_load((FIXTURES / "planted" / "existing-audiences.yml").read_text())
    orphan["identity"]["narrows"] = ["missing-a", "missing-b"]
    (tmp_path / "orphan.yml").write_text(yaml.safe_dump(orphan))
    planted = [tmp_path / "orphan.yml", FIXTURES / "planted" / "schema-conformance.yml"]
    code, output = run(*map(str, [*VALID, *planted]), "-t", str(table), *mode)
    assert code == 1, output
    assert output.splitlines() == [
        f"{table}: error [scope-table-derivable] the scope table is not derived, since 2 audience "
        "records hold errors; ekthesis check reports them",
        f"{table}: not derived",
    ]
    assert table.read_text() == "kept: true\n" if mode else not table.exists()


def test_errors_of_the_records_yield_one_sarif_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """In SARIF, the records with errors yield one result of a rule of its own, at the table."""
    shutil.copy(FIXTURES / "planted" / "existing-audiences.yml", tmp_path / "orphan.yml")
    monkeypatch.chdir(tmp_path)
    code, output = run("orphan.yml", "-t", "scope-table.yml", "--format", "sarif")
    assert code == 1
    log = json.loads(output)
    assert profile_violations(log) == []
    [result] = log["runs"][0]["results"]
    assert result["ruleId"] == "scope-table-derivable"
    assert "1 audience record holds errors" in result["message"]["text"]
    assert result["locations"][0]["logicalLocations"] == [{"name": "path:scope-table.yml"}]
    assert "invocations" not in log["runs"][0]


def test_warnings_of_the_records_are_not_repeated(tmp_path: Path) -> None:
    """The command reports the errors of the records, and leaves their warnings to the check."""
    table = tmp_path / "scope-table.yml"
    record = FIXTURES / "planted" / "undeclared-concepts.yml"
    code, output = run(str(record), "-t", str(table))
    assert code == 0, output
    assert output.splitlines() == [f"{table}: 1 audiences written"]


def test_record_of_another_contract_is_a_usage_error(tmp_path: Path) -> None:
    """A record that is no audience record ends the command with the code of a usage error."""
    exposition = Path(__file__).parent / "fixtures" / "valid.yml"
    code, _ = run(str(exposition), "-t", str(tmp_path / "scope-table.yml"))
    assert code == 2


# --- Structure of a written table ------------------------------------------------------------------


def check_edited(tmp_path: Path, edit: Callable[[dict[str, Any]], None]) -> tuple[int, str]:
    """Write the table of the valid records, apply `edit` to its data, and check it."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    data = yaml.safe_load(table.read_text())
    edit(data)
    table.write_text(yaml.safe_dump(data, sort_keys=False))
    return generate(table, "--check")


@pytest.mark.parametrize(
    ("edit", "line"),
    [
        (
            lambda data: data.pop("sources"),
            ": error [scope-table-current] the scope table lacks the field sources",
        ),
        (
            lambda data: data.update(extra=1),
            ":extra: error [scope-table-current] the scope table holds the field extra",
        ),
        (
            lambda data: data.update(contract="onomasia:scope-table@2"),
            ":contract: error [scope-table-current] the scope table names the contract onomasia:scope-table@2",
        ),
        (
            lambda data: data.update(sources={}),
            ":sources: error [scope-table-current] the sources of the scope table form no list",
        ),
        (
            lambda data: data.update(
                sources=[{"repository": "r", "commit": "abc", "dirty": False}]
            ),
            ":sources[0].commit: error [scope-table-current] the commit of the source 0 is no full commit",
        ),
        (
            lambda data: data.update(
                sources=[{"repository": "r", "commit": "0" * 40, "dirty": "no"}]
            ),
            ":sources[0].dirty: error [scope-table-current] the dirty of the source 0 is no boolean",
        ),
        (
            lambda data: data.update(sources=[{"repository": "r", "commit": "0" * 40}]),
            ":sources[0]: error [scope-table-current] the source 0 lacks the field dirty",
        ),
    ],
    ids=[
        "missing-sources",
        "extra-key",
        "wrong-contract",
        "sources-no-list",
        "short-commit",
        "dirty-no-boolean",
        "source-without-dirty",
    ],
)
def test_check_reports_a_malformed_table(
    tmp_path: Path, edit: Callable[[dict[str, Any]], None], line: str
) -> None:
    """A table that breaks the structure of its contract is stale, with a precise finding."""
    code, output = check_edited(tmp_path, edit)
    assert code == 1, output
    [finding, _] = output.splitlines()
    assert finding.startswith(f"{tmp_path / 'scope-table.yml'}{line}"), finding


def test_check_admits_any_order_of_a_row(tmp_path: Path) -> None:
    """A row listing its relatives in another order holds the same relatives."""

    def reverse(data: dict[str, Any]) -> None:
        data["audiences"]["neuroscientists"]["descendants"].reverse()

    code, output = check_edited(tmp_path, reverse)
    assert code == 0, output


def test_missing_row_is_located_at_the_absent_row(tmp_path: Path) -> None:
    """A missing row has the pointer of that row, and the region of the audiences."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    data = yaml.safe_load(table.read_text())
    data["audiences"].pop("neuroscientists")
    table.write_text(yaml.safe_dump(data, sort_keys=False))
    derived = ScopeTable.derive(load_audience(path) for path in VALID)
    [finding] = derived.differences(table)
    assert finding.absent == "neuroscientists"
    assert finding.locus().pointer() == "/audiences/neuroscientists"


def test_written_table_opens_on_its_header(tmp_path: Path) -> None:
    """A written table states that it is generated."""
    table = tmp_path / "scope-table.yml"
    generate(table)
    assert table.read_text().startswith(HEADER)


def test_table_outside_the_root_is_refused_in_sarif_check(tmp_path: Path) -> None:
    """With `--check --format sarif`, the table is a resource of the log, so it lies under the root."""
    root = tmp_path / "root"
    root.mkdir()
    records = []
    for path in VALID:
        records.append(root / path.name)
        records[-1].write_text(path.read_text())
    table = tmp_path / "elsewhere" / "scope-table.yml"
    assert run(*map(str, records), "-t", str(table), "-r", str(root))[0] == 0
    arguments = ["-t", str(table), "-r", str(root), "--check", "--format", "sarif"]
    code, output = run(*map(str, records), *arguments)
    assert code == 2, output


def test_misspelt_contract_is_a_schema_error(tmp_path: Path) -> None:
    """A record naming no known contract holds an error, as in `ekthesis check`, not a usage error."""
    record = tmp_path / "readers.yml"
    record.write_text(
        (FIXTURES / "valid" / "neuroscientists.yml")
        .read_text()
        .replace("ekthesis:audience@1", "ekthesis:audiense@1")
    )
    code, output = run(str(record), "-t", str(tmp_path / "scope-table.yml"))
    assert code == 1, output
    assert "[scope-table-derivable]" in output
    assert "1 audience record holds errors" in output


# --- Provenance ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "public"),
    [
        ("https://user:token@github.com/org/repo.git", "https://github.com/org/repo.git"),
        ("https://token@example.org:8443/repo", "https://example.org:8443/repo"),
        ("ssh://git@host.org/org/repo.git", "ssh://host.org/org/repo.git"),
        ("git@github.com:org/repo.git", "github.com:org/repo.git"),
        ("https://github.com/org/repo.git", "https://github.com/org/repo.git"),
        ("/path/to/repo", "/path/to/repo"),
    ],
)
def test_public_location_strips_the_user_information(url: str, public: str) -> None:
    """The location of a remote loses its user and its token."""
    assert public_location(url) == public


def git(repository: Path, *arguments: str) -> None:
    """Run one command of Git in `repository`, with a fixed identity and no signing."""
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.org",
            "-c",
            "commit.gpgsign=false",
            *arguments,
        ],
        check=True,
        capture_output=True,
    )


@pytest.mark.skipif(shutil.which("git") is None, reason="the command git is absent")
def test_sources_describe_the_records_alone(tmp_path: Path) -> None:
    """A written table leaves its sources clean, and only a changed record makes them dirty."""
    git(tmp_path, "init", "--quiet")
    git(tmp_path, "remote", "add", "origin", "https://user:token@example.org/consumer.git")
    records = []
    for path in VALID:
        records.append(tmp_path / "audiences" / path.name)
        records[-1].parent.mkdir(exist_ok=True)
        records[-1].write_text(path.read_text())
    git(tmp_path, "add", "audiences")
    git(tmp_path, "commit", "--quiet", "-m", "records")
    table = tmp_path / "scope-table.yml"
    arguments = [*map(str, records), "-t", str(table), "-r", str(tmp_path)]

    def regenerate() -> bytes:
        code, output = run(*arguments)
        assert code == 0, output
        return table.read_bytes()

    first = regenerate()
    assert regenerate() == first, "an untracked table leaves the sources clean"
    git(tmp_path, "add", "scope-table.yml")
    git(tmp_path, "commit", "--quiet", "-m", "table")
    committed = regenerate()
    assert regenerate() == committed, "a committed table leaves the sources clean"
    (tmp_path / "notes.md").write_text("another change\n")
    assert regenerate() == committed, "a change outside the records leaves the sources clean"
    [source] = yaml.safe_load(committed)["sources"]
    assert source["repository"] == "https://example.org/consumer.git"
    assert source["dirty"] is False
    with records[0].open("a", encoding="utf-8") as handle:
        handle.write("# changed\n")
    [source] = yaml.safe_load(regenerate())["sources"]
    assert source["dirty"] is True
    git(tmp_path, "checkout", "--quiet", "--", "audiences")
    assert regenerate() == committed
    (tmp_path / ".gitignore").write_text("ignored/\n")
    ignored = tmp_path / "ignored" / "readers.yml"
    ignored.parent.mkdir()
    ignored.write_text(records[0].read_text())
    code, output = run(*map(str, [*records[1:], ignored]), "-t", str(table), "-r", str(tmp_path))
    assert code == 0, output
    [source] = yaml.safe_load(table.read_text())["sources"]
    assert source["dirty"] is True, "an ignored record lies outside every commit"
