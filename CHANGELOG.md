# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `ekthesis check` and `ekthesis scope-table` take a folder in place of files: a folder stands for the YAML files that it holds directly, in name order.
- The contract `ekthesis:audience@1` of an audience record, with its schema, its skeleton `data/skeletons/audience.yml`, and its export in `specs/schema-resources.yml`.
- `ekthesis check` checks audience records: the rules `unique-audiences`, `existing-audiences` and `acyclic-parents` check the audience records of one run together, and the rule `undeclared-concepts` reports each undeclared concept as a warning.
- The command `ekthesis scope-table` writes the scope table `onomasia:scope-table@1` of a set of audience records, and its option `--check` reports, under the rule `scope-table-current`, a written table that breaks the structure of its contract or differs from the derived one. When some records hold an error, the command derives no table, and reports at the table one finding of the rule `scope-table-derivable` naming the number of those records, whose errors `ekthesis check` reports.

### Changed

- **Breaking:** the contract of an audience record becomes `ekthesis:audience@2`. The fields `identity.representatives[].profile` and `knowledge[].concept` hold logical targets in the form of Anagraphe, a mapping `{repository, id, unit}`: a profile is typed by the contact contracts and names no unit, and a concept is untyped. The schema references the target of Anagraphe by its absolute `$id`; the package ships its schema under `data/resources`, and `specs/schema-resources.yml` selects Anagraphe as a source of resources only. `ekthesis:audience@1` stays in the package until every record has migrated. A record migrates by naming `ekthesis:audience@2` and writing each target as a mapping, such as `profile: {id: sergent_claire}`.
- **Breaking:** the contract of an argument record becomes `ekthesis:exposition@2`. It drops the field `exports` of the exposition and the field `unit` of an idea, and requires the field `kind` on every idea: a referenced idea states the kind of its unit, outside the registry of authored kinds, and an idea without a link under `source` is authored. `ekthesis:exposition@1` stays in the package and in `specs/schema-resources.yml` until every record has migrated, and `ekthesis check` applies the same rules to its records. A record migrates by naming `ekthesis:exposition@2` and stating the kind of each referenced idea.
- The rule `relation-requirements` reports each relation between two referenced ideas that requires a recorded relation as unverified, since `ekthesis` reads no source, and names the kind that each idea states.
- `ekthesis check` takes the root of the paths of a SARIF log from `-r`, `--root`, then from `EKTHESIS_ROOT`, then from the working directory, by the command-line conventions of the workspace.
- `ekthesis check` accepts the short form `-o` of `--output`, and writes the text lines to that file as well as the SARIF log.
- `ekthesis check` applies to each record the rules of its contract: the rules on argument records to `ekthesis:exposition@2` and `ekthesis:exposition@1`, the rules on audiences to `ekthesis:audience@1`, and the schema alone to a contract without rules. A record that breaks its schema skips the rules of its contract, and a record that names no known contract skips the rules of every contract.

### Removed

- **Breaking:** the contract `ekthesis:export@1` of a research export, its schema `export.schema.yaml` and the module `ekthesis.exports`, retired by the decision of `geonexus` on independent research and exposition. `specs/schema-resources.yml` no longer exports the contract.
- **Breaking:** the rules `export-conformance`, `existing-units` and `recorded-relations`, which read the exports that a record named; they leave the rule list of the SARIF log.

### Fixed

- `ekthesis -v` and `ekthesis --version` print the version, where they ended with the error of a missing command.
