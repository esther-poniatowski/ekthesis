"""
Command-line interface for the `ekthesis` package.

Defines commands available via `python -m ekthesis` or `ekthesis` if installed as a script.

Commands
--------
info : Display diagnostic information.
check : Check argument records against their schema and the rules on the provenance of ideas, and
    report the findings as text lines or as a SARIF log (`--format sarif`), written to the standard
    output or to a file (`--output`).

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
from .check import Checker
from .resources import packaged_resources
from .sarif import repository_path, sarif_log

app = typer.Typer(add_completion=False, no_args_is_help=True)


class OutputFormat(StrEnum):
    """Format of the output of `ekthesis check`."""

    TEXT = "text"
    SARIF = "sarif"


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@app.command("check")
def cli_check(
    paths: list[Path] = typer.Argument(..., exists=True, dir_okay=False, help="Records to check."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        help=(
            "Output format: one line per finding and a summary, or one SARIF 2.1.0 log in the "
            "findings profile of Elenchos, whose paths are relative to the working directory."
        ),
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        dir_okay=False,
        help=(
            "File to which the SARIF log is written, with its missing parent directories, in "
            "place of the standard output; valid with --format sarif only."
        ),
    ),
) -> None:
    """Check argument records, and exit non-zero on a blocking finding."""
    if output is not None and output_format is not OutputFormat.SARIF:
        raise typer.BadParameter("requires --format sarif", param_hint="--output")
    checker = Checker(packaged_resources())
    if output_format is OutputFormat.SARIF:
        root = Path.cwd()
        for path in paths:
            try:
                repository_path(path, root)
            except ValueError:
                raise typer.BadParameter(
                    f"{path} lies outside the working directory {root}", param_hint="PATHS"
                ) from None
        reports = [checker.report(path) for path in paths]
        findings = [finding for report in reports for finding in report.findings]
        text = json.dumps(sarif_log(reports, root), indent=2, ensure_ascii=False)
        if output is None:
            typer.echo(text)
        else:
            _write(output, text + "\n")
    else:
        findings = checker.check(paths)
        for finding in findings:
            typer.echo(finding.format())
        blocking = sum(finding.severity.blocking for finding in findings)
        typer.echo(
            f"{len(paths)} records checked: {blocking} errors, {len(findings) - blocking} warnings"
        )
    if any(finding.severity.blocking for finding in findings):
        raise typer.Exit(code=1)


def _write(path: Path, text: str) -> None:
    """Write `text` to `path`, creating its parent directories, or exit with the code 2."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as error:
        typer.echo(f"cannot write the log {path}: {error}", err=True)
        raise typer.Exit(code=2) from None


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show the package version and exit."
    )
) -> None:
    """Root command for the package command-line interface."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()
