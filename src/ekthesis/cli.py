"""
Command-line interface for the `ekthesis` package.

Defines commands available via `python -m ekthesis` or `ekthesis` if installed as a script.

Commands
--------
info : Display diagnostic information.
check : Check argument records against their schema and the rules on the provenance of ideas.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

from pathlib import Path

import typer

from . import info, __version__
from .check import Checker
from .resources import packaged_resources

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@app.command("check")
def cli_check(
    paths: list[Path] = typer.Argument(..., exists=True, dir_okay=False, help="Records to check."),
) -> None:
    """Check argument records, and exit non-zero on a blocking finding."""
    findings = Checker(packaged_resources()).check(paths)
    for finding in findings:
        typer.echo(finding.format())
    blocking = sum(finding.severity.blocking for finding in findings)
    typer.echo(
        f"{len(paths)} records checked: {blocking} errors, {len(findings) - blocking} warnings"
    )
    if blocking:
        raise typer.Exit(code=1)


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
