# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The contract `ekthesis:audience@1` of an audience record, with its schema, its skeleton `data/skeletons/audience.yml`, and its export in `specs/schema-resources.yml`.
- `ekthesis check` checks audience records: the rules `unique-audiences`, `existing-audiences` and `acyclic-parents` check the audience records of one run together, and the rule `undeclared-concepts` reports each undeclared concept as a warning.
- The command `ekthesis scope-table` writes the scope table `onomasia:scope-table@1` of a set of audience records, and its option `--check` reports, under the rule `scope-table-current`, a written table that breaks the structure of its contract or differs from the derived one.

### Changed

- `ekthesis check` takes the root of the paths of a SARIF log from `-r`, `--root`, then from `EKTHESIS_ROOT`, then from the working directory, by the command-line conventions of the workspace.
- `ekthesis check` accepts the short form `-o` of `--output`, and writes the text lines to that file as well as the SARIF log.
- `ekthesis check` applies to each record the rules of its contract: the rules on argument records to `ekthesis:exposition@1`, the rules on audiences to `ekthesis:audience@1`, and the schema alone to `ekthesis:export@1`. A record that breaks its schema skips the rules of its contract, and a record that names no known contract skips the rules of every contract.

### Fixed

- `ekthesis -v` and `ekthesis --version` print the version, where they ended with the error of a missing command.
