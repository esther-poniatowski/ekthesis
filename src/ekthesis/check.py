"""
Check of records against their schema and the rules of their contract.

A record of the contract `ekthesis:exposition@3`, or of its retained version
`ekthesis:exposition@1`, is checked by the rules on the provenance of ideas, a record of
`ekthesis:audience@2` by the rules on audiences, and a record of `ekthesis:constraints@1` by the
rules on the identifiers, the units and the references of its items. The audience records of one
run are also checked together, since their parents and their confused communities name each other.

Classes
-------
RecordReport
    The findings of one record, with the identifier that the record declares and the rules skipped
    on it.
Checker
    Applies the rules to records, with given schemas and registries.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from .audiences import (
    AUDIENCE_CONTRACTS,
    Audience,
    RunEntry,
    read_audience,
    record_findings,
    run_findings,
)
from .findings import Finding
from .layout import FieldPath, SchemaLayout
from .positions import parse, position
from .resources import BINDING_FIELD, Resources
from .rules import (
    CONTRACT_RULES,
    LAYOUT_RULES,
    SCHEMA_CONFORMANCE,
    BoundRecord,
    schema_conformance,
)

SKIPPED_ON_UNKNOWN_CONTRACT: tuple[str, ...] = tuple(
    dict.fromkeys(rule.identifier for rules in CONTRACT_RULES.values() for rule in rules)
)
"""Rules that a record naming no known contract is not checked by: the rules of every contract."""


@dataclass(frozen=True)
class RecordReport:
    """
    The findings of one record, with the identifier that the record declares and the rules skipped
    on it.

    Attributes
    ----------
    path : Path
        Path of the record file.
    identifier : str or None
        Value of the field that the schema of the record declares by `x-identifier` at its root,
        or `None` when the record names no known contract, its schema declares no identifier, or
        the record holds no non-empty text in that field.
    findings : tuple of Finding
        Findings of the record, each with the position of its node, or of the closest existing
        ancestor of that node.
    skipped : tuple of str
        Identifiers of the rules that were not applied to the record, empty when every rule was
        applied. A record that breaks `schema-conformance` skips the other rules of its contract,
        and a record that cannot be read, or names no known contract, skips the rules of every
        contract.
    contract : str or None
        Contract that the record names in its field `_schema`, known or not, or `None` when the
        record cannot be read or names none.
    """

    path: Path
    identifier: str | None
    findings: tuple[Finding, ...]
    skipped: tuple[str, ...] = ()
    contract: str | None = None

    @property
    def breaks_schema(self) -> bool:
        """Whether the record cannot be read or breaks its schema, so that its check is partial."""
        return any(finding.rule == SCHEMA_CONFORMANCE.identifier for finding in self.findings)


@dataclass(frozen=True)
class _Reading:
    """One record of a run, read and checked alone, with its node tree and its audience."""

    report: RecordReport
    node: yaml.Node | None
    audience: Audience | None = None


@dataclass
class Checker:
    """
    Applies the rules to records, with given schemas and registries.

    A record is checked by the rules of its contract only once it conforms to its schema, since
    these rules read its fields through that schema. The audience records of a run are then checked
    together.

    Attributes
    ----------
    resources : Resources
        Schemas and registries against which records are checked.
    """

    resources: Resources
    _layouts: dict[str, SchemaLayout] = field(default_factory=dict, init=False, repr=False)

    def check(self, paths: Iterable[Path]) -> list[Finding]:
        """Return the findings of every record of `paths`, record by record."""
        return [finding for report in self.reports(paths) for finding in report.findings]

    def check_record(self, path: Path) -> list[Finding]:
        """Return the findings of the record at `path`, checked as a run of one record."""
        return list(self.report(path).findings)

    def report(self, path: Path) -> RecordReport:
        """Return the report of the record at `path`, checked as a run of one record."""
        [report] = self.reports([path])
        return report

    def reports(self, paths: Iterable[Path]) -> list[RecordReport]:
        """
        Return the report of each record of `paths`, in order, the records forming one run.

        Each record is first checked alone. The audience records of the run that declare an
        identifier are then checked together, and each finding of that check joins the report of
        the record at fault.
        """
        readings = [self._read(path) for path in paths]
        owners: list[int] = []
        entries: list[RunEntry] = []
        for index, reading in enumerate(readings):
            report = reading.report
            if report.contract in AUDIENCE_CONTRACTS and report.identifier is not None:
                owners.append(index)
                entries.append(RunEntry(report.path, report.identifier, reading.audience))
        added = {owners[position]: found for position, found in run_findings(entries).items()}
        return [
            replace(
                reading.report,
                findings=reading.report.findings
                + tuple(_located(finding, reading.node) for finding in added.get(index, [])),
            )
            for index, reading in enumerate(readings)
        ]

    def _read(self, path: Path) -> _Reading:
        """Read the record at `path`, and check it alone."""
        try:
            data, node = parse(path)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            finding = Finding(
                SCHEMA_CONFORMANCE.identifier,
                path,
                FieldPath(),
                SCHEMA_CONFORMANCE.severity,
                f"cannot read the record: {error}",
            )
            return _Reading(RecordReport(path, None, (finding,), SKIPPED_ON_UNKNOWN_CONTRACT), None)
        named = data.get(BINDING_FIELD) if isinstance(data, Mapping) else None
        contract = named if isinstance(named, str) else None
        findings = list(schema_conformance(path, data, self.resources.schemas))
        audience = None
        if not findings:
            if contract in AUDIENCE_CONTRACTS:
                audience = read_audience(path, data)
                findings.extend(record_findings(audience))
            elif contract is not None and contract in LAYOUT_RULES:
                findings.extend(self._layout_findings(path, data, contract))
        report = RecordReport(
            path,
            self._identifier(data),
            tuple(_located(finding, node) for finding in findings),
            self._skipped(contract, findings),
            contract,
        )
        return _Reading(report, node, audience)

    def _layout_findings(self, path: Path, data: object, contract: str) -> list[Finding]:
        """Return the findings of the rules that read a conforming record of `contract` through
        the layout of its schema."""
        record = BoundRecord(path, data, self._layout(contract), self.resources.registries)
        return [finding for rule in LAYOUT_RULES[contract] for finding in rule(record)]

    def _skipped(self, contract: str | None, findings: list[Finding]) -> tuple[str, ...]:
        """Return the rules skipped on a record of `contract` with the findings `findings`."""
        if all(finding.rule != SCHEMA_CONFORMANCE.identifier for finding in findings):
            return ()
        if contract is None or self.resources.schemas.get(contract) is None:
            return SKIPPED_ON_UNKNOWN_CONTRACT
        return tuple(rule.identifier for rule in CONTRACT_RULES.get(contract, ()))

    def _identifier(self, data: object) -> str | None:
        """Return the identifier that the record `data` declares, if it can be read."""
        contract = data.get(BINDING_FIELD) if isinstance(data, Mapping) else None
        if not isinstance(contract, str) or self.resources.schemas.get(contract) is None:
            return None
        pattern = self._layout(contract).record_identifier
        if pattern is None:
            return None
        values = [value for _, value in pattern.select(data)]
        if len(values) == 1 and isinstance(values[0], str) and values[0]:
            return values[0]
        return None

    def _layout(self, contract: str) -> SchemaLayout:
        """Return the layout of the schema of `contract`, read once."""
        if contract not in self._layouts:
            schema = self.resources.schemas.get(contract)
            assert schema is not None, "a record bound to a layout names a known contract"
            self._layouts[contract] = SchemaLayout.from_schema(schema)
        return self._layouts[contract]


def _located(finding: Finding, node: yaml.Node | None) -> Finding:
    """Return `finding` with the position of its locus in the node tree `node` of its record."""
    return replace(finding, position=position(node, finding.locus()))
