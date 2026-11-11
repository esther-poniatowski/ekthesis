"""
Command-line interface for the `ekthesis` package.

Defines commands available via `python -m ekthesis` or `ekthesis` if installed as a script.

Commands
--------
info : Display diagnostic information.
check : Check argument records and audience records against their schema and the rules of their
    contract, and report the findings as text lines or as a SARIF log (`--format sarif`), written to
    the standard output or to a file (`-o`, `--output`).
scope-table : Derive the scope table of audience records and write it (`-t`, `--table`), or, with
    `--check`, report a written table that differs from the derived one, in the formats of `check`.

The options follow the command-line conventions of the workspace. The root of the paths of a SARIF
log is the option `-r`, `--root`, otherwise the environment variable `EKTHESIS_ROOT`, otherwise the
working directory. Ekthesis reads no configuration file, so it searches no ancestor directory for
one. The exit status is 0 without a blocking finding, 1 with one, and 2 on a usage error.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import json
from enum import StrEnum
from pathlib import Path

import typer

from . import info, __version__
from .audiences import AUDIENCE_CONTRACT, load_audience
from .check import Checker, RecordReport
from .provenance import git_sources
from .resources import packaged_resources
from .sarif import repository_path, sarif_log
from .scope_table import ScopeTable, underived

app = typer.Typer(add_completion=False, no_args_is_help=True)

ROOT_VARIABLE = "EKTHESIS_ROOT"
"""Environment variable that names the root when the option `--root` is absent."""


class OutputFormat(StrEnum):
    """Format of the output of `ekthesis check`."""

    TEXT = "text"
    SARIF = "sarif"


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


FORMAT_OPTION = typer.Option(
    OutputFormat.TEXT,
    "--format",
    help=(
        "Output format: one line per finding and a summary, or one SARIF 2.1.0 log in the "
        "findings profile of Elenchos, whose paths are relative to the root."
    ),
)
OUTPUT_OPTION = typer.Option(
    None,
    "--output",
    "-o",
    dir_okay=False,
    help=(
        "File to which the output is written, with its missing parent directories, in "
        "place of the standard output."
    ),
)
ROOT_OPTION = typer.Option(
    None,
    "--root",
    "-r",
    envvar=ROOT_VARIABLE,
    exists=True,
    file_okay=False,
    help=(
        "Root of the repository, against which a SARIF log writes the path of each record; "
        f"defaults to ${ROOT_VARIABLE}, then to the working directory."
    ),
)


@app.command("check")
def cli_check(
    paths: list[Path] = typer.Argument(..., exists=True, dir_okay=False, help="Records to check."),
    output_format: OutputFormat = FORMAT_OPTION,
    output: Path | None = OUTPUT_OPTION,
    root: Path | None = ROOT_OPTION,
) -> None:
    """Check argument and audience records, and exit with status 1 on a blocking finding."""
    base = _base(root, paths if output_format is OutputFormat.SARIF else [])
    reports = Checker(packaged_resources()).reports(paths)
    findings = [finding for report in reports for finding in report.findings]
    blocking = sum(finding.severity.blocking for finding in findings)
    summary = (
        f"{len(paths)} records checked: {blocking} errors, {len(findings) - blocking} warnings"
    )
    _emit(reports, output_format, output, base, summary)
    if blocking:
        raise typer.Exit(code=1)


@app.command("scope-table")
def cli_scope_table(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    paths: list[Path] = typer.Argument(
        ..., exists=True, dir_okay=False, help="Audience records of the table."
    ),
    table: Path = typer.Option(
        ..., "--table", "-t", dir_okay=False, help="File of the scope table."
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help=(
            "Write nothing, and report a table that differs from the one derived from the records."
        ),
    ),
    output_format: OutputFormat = FORMAT_OPTION,
    output: Path | None = OUTPUT_OPTION,
    root: Path | None = ROOT_OPTION,
) -> None:
    """Derive the scope table of audience records, and write it or check it."""
    base = _base(root, [*paths, table] if output_format is OutputFormat.SARIF else [])
    failing = _failing_records(paths)
    if failing:
        report = RecordReport(table, None, (underived(table, failing),))
        _emit([report], output_format, output, base, f"{table}: not derived")
        raise typer.Exit(code=1)
    derived = ScopeTable.derive(load_audience(path) for path in paths)
    if check:
        stale = RecordReport(table, None, tuple(derived.differences(table)))
        state = f"{len(stale.findings)} differences" if stale.findings else "current"
        summary = f"{table}: {state}, {len(derived.rows)} audiences derived"
        _emit([stale], output_format, output, base, summary)
        if stale.findings:
            raise typer.Exit(code=1)
        return
    _write(table, derived.text(git_sources(base, paths)))
    _emit([], output_format, output, base, f"{table}: {len(derived.rows)} audiences written")


def _failing_records(paths: list[Path]) -> int:
    """
    Check the audience records `paths` as one run, and return how many of them hold an error.

    The findings themselves are left to `ekthesis check`, which reports each of them. A record
    naming a known contract other than the audience contract ends the command with the exit code
    2 of a usage error. A record naming no known contract fails `schema-conformance`, so it counts
    as a record holding an error.
    """
    resources = packaged_resources()
    reports = Checker(resources).reports(paths)
    for report in reports:
        contract = report.contract
        if contract not in (None, AUDIENCE_CONTRACT) and resources.schemas.get(contract):
            raise typer.BadParameter(
                f"{report.path} names the contract {contract}, not {AUDIENCE_CONTRACT}",
                param_hint="PATHS",
            )
    return sum(any(finding.severity.blocking for finding in report.findings) for report in reports)


def _base(root: Path | None, located: list[Path]) -> Path:
    """
    Return the root of the paths of a SARIF log, and refuse each path of `located` outside it.

    The root is `root`, otherwise the working directory. A path outside it ends the command with
    the exit code 2 of a usage error, before any record is checked.
    """
    base = (root or Path.cwd()).resolve()
    for path in located:
        try:
            repository_path(path, base)
        except ValueError:
            raise typer.BadParameter(
                f"{path} lies outside the root {base}", param_hint="PATHS"
            ) from None
    return base


def _emit(
    reports: list[RecordReport],
    output_format: OutputFormat,
    output: Path | None,
    base: Path,
    summary: str,
) -> None:
    """Write the findings of `reports`, as text lines closed by `summary` or as a SARIF log."""
    if output_format is OutputFormat.SARIF:
        lines = [json.dumps(sarif_log(reports, base), indent=2, ensure_ascii=False)]
    else:
        lines = [finding.format() for report in reports for finding in report.findings]
        lines.append(summary)
    if output is None:
        for line in lines:
            typer.echo(line)
    else:
        _write(output, "".join(f"{line}\n" for line in lines))


def _write(path: Path, text: str) -> None:
    """Write `text` to `path`, creating its parent directories, or exit with the code 2."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as error:
        typer.echo(f"cannot write the output {path}: {error}", err=True)
        raise typer.Exit(code=2) from None


def _print_version(value: bool) -> None:
    """Print the version and exit, before the group requires a command."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(  # pylint: disable=unused-argument
        False,
        "--version",
        "-v",
        is_eager=True,
        callback=_print_version,
        help="Show the package version and exit.",
    )
) -> None:
    """Root command for the package command-line interface."""
