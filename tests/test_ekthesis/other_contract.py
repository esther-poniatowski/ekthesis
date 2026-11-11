"""A contract that no rule of ekthesis reads, for the tests of a record checked by its schema alone."""

from pathlib import Path

import yaml

from ekthesis.resources import Resources, SchemaCatalog, packaged_resources

OTHER_CONTRACT = "ekthesis:other@1"
"""Contract bound by the schema that `contract_without_rules` writes."""


def contract_without_rules(directory: Path) -> Resources:
    """Return the packaged registries with one schema, of a contract that no rule reads."""
    schemas = directory / "schemas"
    schemas.mkdir()
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["_schema"],
        "properties": {"_schema": {"const": OTHER_CONTRACT}},
    }
    (schemas / "other.schema.yaml").write_text(yaml.safe_dump(schema))
    return Resources(SchemaCatalog.from_directory(schemas), packaged_resources().registries)
