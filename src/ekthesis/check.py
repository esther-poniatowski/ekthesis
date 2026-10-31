"""
Check of argument records against their schema and the rules on the provenance of ideas.

Classes
-------
Checker
    Applies the rules to records, with given schemas and registries.
"""
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .findings import Finding, Severity
from .layout import SchemaLayout
from .resources import BINDING_FIELD, Resources
from .rules import RECORD_RULES, BoundRecord, schema_conformance


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
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            return [Finding("schema-conformance", path, "", Severity.ERROR, f"cannot read the record: {error}")]
        findings = list(schema_conformance(path, data, self.resources.schemas))
        if findings:
            return findings
        record = BoundRecord(path, data, self._layout(data[BINDING_FIELD]), self.resources.registries)
        for rule in RECORD_RULES:
            findings.extend(rule(record))
        return findings

    def _layout(self, contract: str) -> SchemaLayout:
        if contract not in self._layouts:
            schema = self.resources.schemas.get(contract)
            assert schema is not None, "a conforming record names a known contract"
            self._layouts[contract] = SchemaLayout.from_schema(schema)
        return self._layouts[contract]
