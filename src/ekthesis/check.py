"""
Check of argument records against their schema and the rules on the provenance of ideas.

Classes
-------
RecordReport
    The findings of one record, with the identifier that the record declares.
Checker
    Applies the rules to records, with given schemas and registries.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from .findings import Finding, Position
from .layout import FieldPath, SchemaLayout
from .resources import BINDING_FIELD, Resources
from .rules import RECORD_RULES, SCHEMA_CONFORMANCE, BoundRecord, schema_conformance


@dataclass(frozen=True)
class RecordReport:
    """
    The findings of one record, with the identifier that the record declares.

    Attributes
    ----------
    path : Path
        Path of the record file.
    identifier : str or None
        Value of the field that the schema of the record declares by `x-identifier` at its root,
        or `None` when the record names no known contract, its schema declares no identifier, or
        the record holds no non-empty text in that field.
    findings : tuple of Finding
        Findings of the record, each with the position of its node when the node is located.
    """

    path: Path
    identifier: str | None
    findings: tuple[Finding, ...]


@dataclass
class Checker:
    """
    Applies the rules to records, with given schemas and registries.

    A record is checked by the rules of the provenance of ideas only once it conforms to its schema,
    since these rules read its fields through the layout of that schema.

    Attributes
    ----------
    resources : Resources
        Schemas and registries against which records are checked.
    """

    resources: Resources
    _layouts: dict[str, SchemaLayout] = field(default_factory=dict, init=False, repr=False)

    def check(self, paths: Iterable[Path]) -> list[Finding]:
        """Return the findings of every record of `paths`, record by record."""
        return [finding for path in paths for finding in self.check_record(path)]

    def check_record(self, path: Path) -> list[Finding]:
        """Return the findings of the record at `path`."""
        return list(self.report(path).findings)

    def report(self, path: Path) -> RecordReport:
        """Return the findings of the record at `path`, with the identifier that it declares."""
        try:
            data, node = _parse(path)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            finding = Finding(
                SCHEMA_CONFORMANCE.identifier,
                path,
                FieldPath(),
                SCHEMA_CONFORMANCE.severity,
                f"cannot read the record: {error}",
            )
            return RecordReport(path, None, (finding,))
        findings = tuple(
            replace(finding, position=_position(node, finding.field))
            for finding in self._findings(path, data)
        )
        return RecordReport(path, self._identifier(data), findings)

    def _findings(self, path: Path, data: object) -> list[Finding]:
        """Return the findings of the record `data` read from `path`."""
        findings = list(schema_conformance(path, data, self.resources.schemas))
        if findings:
            return findings
        assert isinstance(data, Mapping), "a conforming record is a mapping"
        record = BoundRecord(
            path, data, self._layout(data[BINDING_FIELD]), self.resources.registries
        )
        for rule in RECORD_RULES:
            findings.extend(rule(record))
        return findings

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


def _parse(path: Path) -> tuple[object, yaml.Node | None]:
    """Parse the record at `path` as `yaml.safe_load` does, and return its node tree as well."""
    loader = yaml.SafeLoader(path.read_text(encoding="utf-8"))
    try:
        node = loader.get_single_node()
        return (loader.construct_document(node) if node is not None else None), node
    finally:
        loader.dispose()


def _position(node: yaml.Node | None, at: FieldPath) -> Position | None:
    """
    Return where the node at `at` starts in the tree `node`, or `None` for the root path.

    A key is matched by its text as written, and the last of two equal keys is kept, as the
    loader keeps it. A path that leaves the tree yields `None`.
    """
    if node is None or not at.segments:
        return None
    current: yaml.Node = node
    for segment in at.segments:
        if isinstance(current, yaml.SequenceNode) and isinstance(segment, int):
            if not 0 <= segment < len(current.value):
                return None
            current = current.value[segment]
        elif isinstance(current, yaml.MappingNode):
            values = [
                value
                for key, value in current.value
                if isinstance(key, yaml.ScalarNode) and key.value == str(segment)
            ]
            if not values:
                return None
            current = values[-1]
        else:
            return None
    return Position(current.start_mark.line + 1, current.start_mark.column + 1)
