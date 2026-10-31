"""
Findings reported by the check of an argument record.

Classes
-------
Severity
    Severity of a finding, which decides whether it blocks.
Finding
    One violation of a rule, located in a record.

Notes
-----
The fields of a finding map one to one onto a result of SARIF: `rule` onto `ruleId`, `record` onto
the artifact location, `field` onto the logical location, `severity` onto `level`, and `message`
onto `message.text`. A SARIF output therefore changes only the serialization.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    """Severity of a finding: an error blocks the check, a warning does not."""

    ERROR = "error"
    WARNING = "warning"

    @property
    def blocking(self) -> bool:
        """Whether a finding of this severity makes the check fail."""
        return self is Severity.ERROR


@dataclass(frozen=True)
class Finding:
    """
    One violation of a rule, located in a record.

    Attributes
    ----------
    rule : str
        Identifier of the violated rule.
    record : Path
        Path of the record holding the violation.
    field : str
        Field path of the node at fault, in the syntax of Ekphrasis (`relations[2].target`), or the
        empty string for the whole record.
    severity : Severity
        Severity of the finding.
    message : str
        Explanation of the violation, naming the values at fault.
    """

    rule: str
    record: Path
    field: str
    severity: Severity
    message: str

    def format(self) -> str:
        """Format the finding on one line, as `record:field: severity [rule] message`."""
        location = f"{self.record}:{self.field}" if self.field else str(self.record)
        return f"{location}: {self.severity} [{self.rule}] {self.message}"
