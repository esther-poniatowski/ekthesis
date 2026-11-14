# ekthesis

[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Specifies how an author arranges an argument for an audience: the selection and order of its ideas, their rhetorical relations, glossaries and audiences.

---

## Overview

An exposition, such as an article, a talk, a course or a poster, presents ideas to a reader. `ekthesis` answers one root question:

> How can the content of a source, such as the records of a research inquiry, be presented to various audiences and in various formats?

`ekthesis` specifies the records of an exposition independently of the activity that produced its ideas. An idea either references a unit of an external source and states the kind of that unit, or is an authored idea of a declared kind.

### Motivation

An argument written as prose alone gives no handle on two questions:

- which source supports each claim, and which relation a source must record for each relation asserted between two claims;
- which ideas, names and symbols suit a given audience and venue.

Research records, such as those of [`gnomon`](https://github.com/esther-poniatowski/gnomon), answer neither question, since research does not depend on a reader. `ekthesis` answers both for any argument, whether or not research produced its ideas.

### Status

Pre-alpha. The package provides the contract `ekthesis:exposition@3` of an argument record, with its earlier version `ekthesis:exposition@1` retained until every record has migrated, the contract `ekthesis:audience@2` of an audience record and the contract `ekthesis:constraints@1` of the constraints of a venue, each with its skeleton, the closed registries of authored kinds and of rhetorical relations, and a command that checks records against them:

```sh
ekthesis check path/to/argument.yml
```

The command reports each finding with its rule, its field and its severity. Ekthesis reads no source, so it reports each relation between two referenced ideas that requires a recorded relation as unverified, at the severity of a warning; the [decision on the argument record](docs/adr/argument-record.md) states the form of a record. The audience records passed to one run are checked together. Each parent and each confused community that an audience names must be an audience record of the run, no two records may declare one identifier, and no chain of parents may return to its audience. Each concept named under `undeclared` is reported as a warning. A concept and the contact profile of a representative are named by logical targets of Anagraphe, whose form the schema checks and whose record Anagraphe resolves. The optional field `metadata` is reserved to the consumer, and Ekthesis does not check it. The [decision on audiences](docs/adr/audiences.md) states the content of an audience record. In a constraints record, no two groups, sources or constraints may share an identifier, and each source and each group that a constraint names must be declared by the record. The record of an exposition names its constraints record by a logical target, which Anagraphe resolves; the [decision on venue constraints](docs/adr/constraints.md) states the content of a constraints record. The exit status is 0 without an error, 1 with an error, and 2 on a usage error. The option `--format sarif` replaces these lines with one SARIF 2.1.0 log in the [findings profile of Elenchos](https://github.com/esther-poniatowski/elenchos/blob/main/docs/profile.md), the format read by the gate Elenchos. The output goes to the standard output, or to the file named by `-o`, `--output`, which a command run without a shell needs:

```sh
ekthesis check --format sarif -o build/findings.sarif path/to/argument.yml
```

The log writes the path of each record relative to the root of the repository, so every record must lie under the root. The root is the option `-r`, `--root PATH`, otherwise the environment variable `EKTHESIS_ROOT`, otherwise the working directory. Ekthesis reads no configuration file, so it searches no ancestor directory for one. A record that breaks its schema is checked by no other rule, and the log then declares its run incomplete. The exit status does not depend on the format. The option `-v`, `--version` prints the version. The [decision on the SARIF output](docs/adr/sarif-output.md) states how each finding maps onto a result.

The command `ekthesis scope-table` derives the scope table of a set of audience records, in the contract `onomasia:scope-table@1` that Onomasia reads to decide which lexical rules bind a text. The ancestors of an audience are the transitive closure of its parents, and its descendants are the transitive closure of the inverse relation. The command writes the table to the file named by `-t`, `--table`:

```sh
ekthesis scope-table audiences -t build/scope-table.yml
```

The table lists its audiences and their relatives in sorted order. Its field `sources` names the repository holding the root, by its remote without user information, with the commit checked out and whether the records read hold uncommitted changes; it is empty when the root lies in no Git repository. Therefore, unchanged records at one commit yield identical bytes, whatever the state of the table itself. With the option `--check`, the command writes nothing, and reports with the exit status 1 a written table that breaks the structure of its contract, or a row that holds other ancestors or descendants than the derived row, in any order. That comparison leaves the values of `sources` aside, since every commit changes them. When some records hold an error, the command writes nothing and exits with the status 1, in both modes. It then reports one finding of the rule `scope-table-derivable` at the table, which names the number of those records; `ekthesis check` reports their errors, so a gate that runs both commands reports each error once. It takes `--format`, `-o`, `--output` and `-r`, `--root` as `ekthesis check` does. Both commands take files or folders: a folder stands for the files ending in `.yml` or `.yaml` that it holds directly, in name order, so a gate that runs without a shell names the folder of its records.

The repository also holds the decisions, theory notes and proposals carried from `gnomon` with their history. The [decision of `gnomon` on its scope](https://github.com/esther-poniatowski/gnomon/blob/45de45d9f362ffc6340cba3837cd44a46cd3b172/docs/adr/research-scope.md) states the boundary between the two tools.

---

## Documentation

The [documentation index](docs/_index.md) is the entry point.

Open goals, the open design decisions included, are recorded in the [project goals](TODO.md).

---

## Contributing

Contributions follow the [contribution guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
