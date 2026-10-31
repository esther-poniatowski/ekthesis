"""
Findings reported by the check of an argument record.

Classes
-------
Severity
    Severity of a finding, which decides whether it blocks.
Rule
    Identifier, summary and severity of a rule of the check.
Position
    Line and column at which the node of a finding starts in its record.
Finding
    One violation of a rule, located in a record.

Notes
-----
The fields of a finding map onto a result of SARIF: `rule` onto `ruleId`, `record` onto the
artifact location, `position` onto its region, the locus of the finding (`field`, extended by
`absent` when given) onto the locus of the logical location, `severity` onto `level`, `message` onto
`message.text`, and `discriminator` onto the partial fingerprint `discriminator/v1`. The module
`ekthesis.sarif` writes that serialization.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .layout import FieldPath


class Severity(StrEnum):
    """Severity of a finding: an error blocks the check, a warning does not."""

    ERROR = "error"
    WARNING = "warning"

    @property
    def blocking(self) -> bool:
        """Whether a finding of this severity makes the check fail."""
        return self is Severity.ERROR


@dataclass(frozen=True)
class Rule:
    """
    Rule of the check, with the severity of its findings.

    Attributes
    ----------
    identifier : str
        Stable identifier of the rule, in lower kebab-case.
    summary : str
        One sentence stating what the rule requires of a record.
    severity : Severity
        Severity of every finding of the rule.
    """

    identifier: str
    summary: str
    severity: Severity


@dataclass(frozen=True)
class Position:
    """Line and column, both counted from 1 in Unicode code points, at which a node starts."""

    line: int
    column: int


@dataclass(frozen=True)
class Finding:  # pylint: disable=too-many-instance-attributes  # one per field of a result
    """
    One violation of a rule, located in a record.

    Attributes
    ----------
    rule : str
        Identifier of the violated rule.
    record : Path
        Path of the record holding the violation.
    field : FieldPath
        Field path of the node at fault, printed in the syntax of Ekphrasis (`relations[2].target`),
        or the root path for the whole record.
    severity : Severity
        Severity of the finding.
    message : str
        Explanation of the violation, naming the values at fault.
    discriminator : str
        Offending content that separates this finding from another finding of its rule at the same
        field, or the empty string when the rule yields at most one finding per field.
    position : Position or None
        Start of the node at the locus of the finding in the record file, or of its closest
        existing ancestor when the record does not hold that node; `None` when that node is the
        whole record.
    absent : str or None
        Name of a property that the node at `field` lacks, when the finding concerns that absent
        property, as a missing required property; `None` otherwise. The text line prints `field`
        alone, and the locus of the finding extends `field` by this name.
    """

    rule: str
    record: Path
    field: FieldPath
    severity: Severity
    message: str
    discriminator: str = ""
    position: Position | None = None
    absent: str | None = None

    def locus(self) -> FieldPath:
        """Return the field path of the node that the finding concerns, absent or not."""
        return self.field if self.absent is None else self.field.child(self.absent)

    def format(self) -> str:
        """Format the finding on one line, as `record:field: severity [rule] message`."""
        field = str(self.field)
        location = f"{self.record}:{field}" if field else str(self.record)
        return f"{location}: {self.severity} [{self.rule}] {self.message}"
