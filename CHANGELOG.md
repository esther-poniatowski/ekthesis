# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The rule `distinct-keys` of `ekthesis check` reports a key that a mapping of a record repeats, at the repeated key, whatever the contract of the record. The YAML parser keeps the last of two equal keys and drops the earlier value, so the rule reads the node tree of the record.
- `ekthesis check` and `ekthesis scope-table` take a folder in place of files: a folder stands for the YAML files that it holds directly, in name order.
- The contract of an audience record, with its schema, its skeleton `data/skeletons/audience.yml`, and its export in `specs/schema-resources.yml`. Its first version, `ekthesis:audience@1`, wrote its logical targets as text; it is retired, since every record has migrated to `ekthesis:audience@2`.
- The contract `ekthesis:constraints@1` of the constraints that a venue imposes on one kind of exposition, with its schema, its skeleton `data/skeletons/constraints.yml`, and its export in `specs/schema-resources.yml`. A record declares its sources once, and each constraint states its requirement and the sources that state it, with an optional group.
- `ekthesis check` checks constraints records: after the schema, the rule `unique-identifiers` checks the identifiers within each of their groups, sources and constraints, the new rule `unique-units` reports an identifier shared by two of these collections, since the units of one record share one namespace, and the rule `existing-references` checks the groups and the sources that each constraint names.
- The field `venue-constraints` of `ekthesis:exposition@3` accepts the logical target of a constraints record, typed by `x-target-contract: ['ekthesis:constraints']` and naming no unit, beside the link that it held before; every valid record stays valid, so the contract keeps its version. Anagraphe resolves the target and reports a record of another contract.
- `ekthesis check` checks audience records: the rules `unique-audiences`, `existing-audiences` and `acyclic-parents` check the audience records of one run together, and the rule `undeclared-concepts` reports each undeclared concept as a warning.
- The command `ekthesis scope-table` writes the scope table `onomasia:scope-table@1` of a set of audience records, and its option `--check` reports, under the rule `scope-table-current`, a written table that breaks the structure of its contract or differs from the derived one. When some records hold an error, the command derives no table, and reports at the table one finding of the rule `scope-table-derivable` naming the number of those records, whose errors `ekthesis check` reports.

### Changed

- **Breaking:** the configuration of Kleisis moves from `specs/schema-resources.yml` to `config/tools/kleisis.yml`, of format `kleisis:configuration@1`, which Kleisis finds through `hodegos.yml`. It declares the keywords `x-registry` and `x-role`, the only keywords to which Ekthesis gives a meaning. It names three dependencies: Anagraphe, for the addressing schema and the keywords `x-identifier` and `x-target-contract`; Ekphrasis, for the keyword `x-kind`; and Onomasia, for the contract `onomasia:scope-table@1`. A consumer that read the former record reads the configuration instead.
- `ekthesis` prints, converts and matches its field paths through `anagraphe-read`, a new dependency, pinned by commit in `environment.yml`. A text line prints a field path as the field-path specification of Anagraphe prints it: a key that a bare key cannot hold, such as a key holding a space or a quote, is written in brackets as a JSON string with its escapes. The JSON Pointer of a locus is unchanged.
- The schemas of `ekthesis:exposition@3`, `ekthesis:exposition@1` and `ekthesis:constraints@1` drop the keyword `x-refers`. A field that names an item of its record references the identifier field of the definition of that item, such as `#/$defs/idea/properties/id`, from which the check reads the collection of the item. The validation of every record is unchanged, so each contract keeps its version.
- **Breaking:** the contract of an audience record becomes `ekthesis:audience@2`. The fields `identity.representatives[].profile` and `knowledge[].concept` hold logical targets in the form of Anagraphe, a mapping `{repository, id, unit}`: a profile names no unit, and leaves the contract of its record open for the consumer to narrow, and a concept is untyped. The schema references the target of Anagraphe by its absolute `$id`; the check reads that schema from `anagraphe-read`, and the configuration of Kleisis selects Anagraphe as a source of resources only. A record migrates by naming `ekthesis:audience@2` and writing each target as a mapping, such as `profile: {id: doe_jane}`.
- **Breaking:** the contract of an argument record becomes `ekthesis:exposition@3`. It drops the field `exports` of the exposition and the field `unit` of an idea, and requires the field `kind` on every idea: a referenced idea states the kind of its unit, outside the registry of authored kinds, and an idea without a `source` is authored. The `source` of a referenced idea is a logical target of Anagraphe, such as `{id: mixture-input, unit: definition}`, whose existence `anagraphe targets check` verifies. `ekthesis:exposition@1` stays in the package and in `specs/schema-resources.yml` until every record has migrated, and `ekthesis check` applies the same rules to its records. A record migrates by naming `ekthesis:exposition@3`, stating the kind of each referenced idea, and writing each source as a logical target.
- The rule `relation-requirements` reports each relation between two referenced ideas that requires a recorded relation as unverified, since `ekthesis` reads no source, and names the kind that each idea states.
- `ekthesis check` takes the root of the paths of a SARIF log from `-r`, `--root`, then from `EKTHESIS_ROOT`, then from the working directory, by the command-line conventions of the workspace.
- `ekthesis check` accepts the short form `-o` of `--output`, and writes the text lines to that file as well as the SARIF log.
- `ekthesis check` applies to each record the rules of its contract: the rules on argument records to `ekthesis:exposition@3` and `ekthesis:exposition@1`, the rules on audiences to `ekthesis:audience@2`, and the schema alone to a contract without rules. A record that breaks its schema skips the rules of its contract, and a record that names no known contract skips the rules of every contract.

### Removed

- The copy of the addressing schema of Anagraphe under `data/resources`, whose bytes differed from those of Anagraphe under the same `$id`. The check reads the schema from `anagraphe-read`, at the commit from which Kleisis materializes the same resource.
- **Breaking:** the rule `source-links` and the module `ekthesis.links`. `ekthesis check` resolves no link to a source, since Anagraphe checks the destination of each link, and admits no heading anchor that Anagraphe rejects. The schema of `ekthesis:exposition@1` drops the keyword `x-resolves`, and keeps its validation.
- **Breaking:** the contract `ekthesis:export@1` of a research export, its schema `export.schema.yaml` and the module `ekthesis.exports`, retired by the decision of `geonexus` on independent research and exposition. `specs/schema-resources.yml` no longer exports the contract.
- **Breaking:** the rules `export-conformance`, `existing-units` and `recorded-relations`, which read the exports that a record named; they leave the rule list of the SARIF log.

### Fixed

- `ekthesis -v` and `ekthesis --version` print the version, where they ended with the error of a missing command.
