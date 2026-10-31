"""
Serialization of the findings of a check as one SARIF 2.1.0 log, in the findings profile of the
gate Elenchos.

The profile fixes the subset of SARIF that a producer writes, so that the gate Elenchos can build a
stable identity for each finding from its tool, rule, resource, locus and discriminator. The log
holds one run, whose results map the fields of each finding as follows:

- `rule` onto `ruleId`, and `severity` onto `level`, always written;
- `message` onto `message.text`;
- `record` onto the artifact location, relative to the root and based on `SRCROOT`, and `position`
  onto its region, absent for a finding on the whole record;
- the record and `field` onto the name of the single logical location, `<resource>#<locus>`: the
  resource is `id:<identifier>` when the record declares an identifier, `path:<path>` otherwise,
  and the locus is the JSON Pointer of the field, empty for the whole record;
- `discriminator` onto `partialFingerprints["discriminator/v1"]`, when it is non-empty.

The gate alone writes `fingerprints` and `suppressions`, so the log holds neither.

Functions
---------
repository_path(path, root) -> str
    Path of a record relative to the root, in POSIX form.
logical_name(resource, locus) -> str
    Name of a logical location, joining a resource and a locus.
sarif_log(reports, root) -> dict
    SARIF log of the reports of a check.

Attributes
----------
SARIF_SCHEMA : str
    URI of the SARIF 2.1.0 schema of errata 01.
"""

from collections.abc import Iterable
from pathlib import Path
from urllib.parse import quote

from . import __version__
from .check import RecordReport
from .findings import Finding
from .rules import RULES

SARIF_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)

TOOL_NAME = "ekthesis"
"""Name of the driver, the first component of the identity of each finding."""

URI_BASE = "SRCROOT"
"""Base of every artifact URI, standing for the root of the consumer repository."""

JsonObject = dict[str, object]


def repository_path(path: Path, root: Path) -> str:
    """
    Return the path of the record `path` relative to `root`, in POSIX form.

    Parameters
    ----------
    path : Path
        Path of a record, absolute or relative to the working directory.
    root : Path
        Root of the repository.

    Returns
    -------
    str
        Relative path, with no leading `/` or `./` and no `.` or `..` segment.

    Raises
    ------
    ValueError
        If the record lies outside `root`.
    """
    return path.resolve().relative_to(root.resolve()).as_posix()


def logical_name(resource: str, locus: str) -> str:
    """
    Return the name of a logical location, `<resource>` or `<resource>#<locus>`.

    The resource escapes `%` as `%25` and `#` as `%23`, so that the name splits at its first `#`;
    the locus is written as is.

    Examples
    --------
    >>> logical_name("path:docs/notes#old.yml", "/ideas/0")
    'path:docs/notes%23old.yml#/ideas/0'
    >>> logical_name("id:poster", "")
    'id:poster'
    """
    escaped = resource.replace("%", "%25").replace("#", "%23")
    return f"{escaped}#{locus}" if locus else escaped


def sarif_log(reports: Iterable[RecordReport], root: Path) -> JsonObject:
    """
    Return the SARIF log of the reports of one check, as a JSON object.

    Parameters
    ----------
    reports : Iterable[RecordReport]
        Report of each checked record, in the order of the check.
    root : Path
        Root of the repository, against which the path of each record is written.

    Returns
    -------
    dict
        Log holding one run of the driver `ekthesis`.

    Raises
    ------
    ValueError
        If a record lies outside `root`.
    """
    results = [
        _result(finding, _resource(report, root), repository_path(report.path, root))
        for report in reports
        for finding in report.findings
    ]
    return {
        "version": "2.1.0",
        "$schema": SARIF_SCHEMA,
        "runs": [
            {"tool": {"driver": _driver()}, "columnKind": "unicodeCodePoints", "results": results}
        ],
    }


def _driver() -> JsonObject:
    """Describe the driver `ekthesis`, with every rule of the check."""
    return {
        "name": TOOL_NAME,
        "version": __version__,
        "rules": [
            {
                "id": rule.identifier,
                "shortDescription": {"text": rule.summary},
                "defaultConfiguration": {"level": str(rule.severity)},
            }
            for rule in RULES
        ],
    }


def _resource(report: RecordReport, root: Path) -> str:
    """Return the resource of a record: its declared identifier, or else its relative path."""
    if report.identifier is not None:
        return f"id:{report.identifier}"
    return f"path:{repository_path(report.path, root)}"


def _result(finding: Finding, resource: str, path: str) -> JsonObject:
    """Return the SARIF result of `finding`, in a record of given resource and relative path."""
    physical: JsonObject = {
        "artifactLocation": {"uri": quote(path, safe="/"), "uriBaseId": URI_BASE}
    }
    if finding.position is not None:
        physical["region"] = {
            "startLine": finding.position.line,
            "startColumn": finding.position.column,
        }
    result: JsonObject = {
        "ruleId": finding.rule,
        "level": str(finding.severity),
        "message": {"text": finding.message},
        "locations": [
            {
                "physicalLocation": physical,
                "logicalLocations": [{"name": logical_name(resource, finding.field.pointer())}],
            }
        ],
    }
    if finding.discriminator:
        result["partialFingerprints"] = {"discriminator/v1": finding.discriminator}
    return result
