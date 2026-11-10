"""
Command-line interface for the `ekthesis` package.

Defines commands available via `python -m ekthesis` or `ekthesis` if installed as a script.

Commands
--------
info : Display diagnostic information.
check : Check argument records against their schema and the rules on the provenance of ideas, and
    report the findings as text lines or as a SARIF log (`--format sarif`), written to the standard
    output or to a file (`-o`, `--output`).

The options follow the command-line conventions of the workspace. The root of the paths of a SARIF
log is the option `-r`, `--root`, otherwise the environment variable `EKTHESIS_ROOT`, otherwise the
working directory. Ekthesis reads no settings file, so it searches no ancestor directory for one.
The exit status is 0 without a blocking finding, 1 with one, and 2 on a usage error.

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
        "-o",
        dir_okay=False,
        help=(
            "File to which the output is written, with its missing parent directories, in "
            "place of the standard output."
        ),
    ),
    root: Path | None = typer.Option(
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
    ),
) -> None:
    """Check argument records, and exit with status 1 on a blocking finding."""
    checker = Checker(packaged_resources())
    if output_format is OutputFormat.SARIF:
        base = (root or Path.cwd()).resolve()
        for path in paths:
            try:
                repository_path(path, base)
            except ValueError:
                raise typer.BadParameter(
                    f"{path} lies outside the root {base}", param_hint="PATHS"
                ) from None
        reports = [checker.report(path) for path in paths]
        findings = [finding for report in reports for finding in report.findings]
        lines = [json.dumps(sarif_log(reports, base), indent=2, ensure_ascii=False)]
    else:
        findings = checker.check(paths)
        blocking = sum(finding.severity.blocking for finding in findings)
        lines = [finding.format() for finding in findings]
        lines.append(
            f"{len(paths)} records checked: {blocking} errors, {len(findings) - blocking} warnings"
        )
    if output is None:
        for line in lines:
            typer.echo(line)
    else:
        _write(output, "".join(f"{line}\n" for line in lines))
    if any(finding.severity.blocking for finding in findings):
        raise typer.Exit(code=1)


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
