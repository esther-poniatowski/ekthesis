# ekthesis

[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Specifies how an author arranges an argument for an audience: the selection and order of its ideas, their rhetorical relations, glossaries and audiences.

---

## Overview

An exposition, such as an article, a talk, a course or a poster, presents ideas to a reader. `ekthesis` specifies the records of an exposition independently of the activity that produced its ideas. An idea either references a unit of an external source, read through a published contract, or is an authored idea of a declared kind.

### Motivation

An argument written as prose alone gives no handle on two questions:

- which source supports each claim, and whether a relation asserted between two claims holds in that source;
- which ideas, names and symbols suit a given audience and venue.

Research records, such as those of [`gnomon`](https://github.com/esther-poniatowski/gnomon), answer neither question, since research does not depend on a reader. `ekthesis` answers both for any argument, whether or not research produced its ideas.

### Status

Pre-alpha. The package provides the contract `ekthesis:exposition@1` of an argument record, the closed registries of authored kinds and of rhetorical relations, and a command that checks records against them:

```sh
ekthesis check path/to/argument.yml
```

The command reports each finding with its rule, its field and its severity, and exits with a nonzero code on an error. The option `--format sarif` replaces these lines with one SARIF 2.1.0 log in the [findings profile of Elenchos](https://github.com/esther-poniatowski/elenchos/blob/main/docs/profile.md), the format read by the gate Elenchos. The log goes to the standard output, or to the file named by `--output`, which a command run without a shell needs:

```sh
ekthesis check --format sarif --output build/findings.sarif path/to/argument.yml
```

The log writes the path of each record relative to the working directory, so every record must lie under that directory. A record that breaks its schema is checked by no other rule, and the log then declares its run incomplete. The exit code does not depend on the format. The [decision on the SARIF output](docs/adr/sarif-output.md) states how each finding maps onto a result.

The repository also holds the decisions, theory notes and proposals carried from `gnomon` with their history. The [decision of `gnomon` on its scope](https://github.com/esther-poniatowski/gnomon/blob/45de45d9f362ffc6340cba3837cd44a46cd3b172/docs/adr/research-scope.md) states the boundary between the two tools.

---

## Documentation

The [documentation index](docs/_index.md) is the entry point.

---

## Contributing

Contributions follow the [contribution guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
