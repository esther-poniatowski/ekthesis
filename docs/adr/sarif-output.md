---
tags:
  - decision
status: proposed
created: 2026-10-31
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - SARIF output of the check
---
# SARIF output of the check

> [!QUESTION] Goal: how does a finding of `ekthesis check` become a result of the findings profile of Elenchos, where the profile leaves the mapping open?

The [findings profile](https://github.com/esther-poniatowski/elenchos/blob/main/docs/profile.md) fixes the subset of SARIF 2.1.0 that a producer writes, and the identity `tool|ruleId|resource|locus|discriminator` that the gate builds from it. The option `ekthesis check --format sarif` writes that log. Four inputs of the identity depend on choices of the producer: the root of the paths, the resource, the discriminator and the region. The producer also decides when its run is complete, and where its log is written.

## Decision

**Root.** The working directory stands for the root `SRCROOT` of the repository. Each artifact URI and each resource `path:` is the path of the record relative to that directory. A record outside the working directory has no such path, so the command refuses it with the exit code 2 of a usage error, before checking any record. ^root

**Resource.** The resource is `id:<identifier>` when three conditions hold:

- the record names a known contract;
- the schema of that contract declares `x-identifier` at its root;
- the record holds a non-empty text in the declared field.

Otherwise the resource is `path:<path>`. The identifier is read even when the record breaks its schema elsewhere. Therefore, an error in another field leaves the resource of the record unchanged. ^resource

**Locus.** The locus is the JSON Pointer of the field of the finding, converted from its segments, so that a key holding `.`, `/` or `~` converts exactly. A finding on the whole record has the empty locus. A missing required property is a field absent from the record: its locus is the pointer of that property (`/ideas/2/statement`), although its text line prints the object that lacks it (`ideas[2]`). ^locus

**Discriminator.** The rule decides whether its findings carry a discriminator, independently of the other findings of the log. Every finding of `schema-conformance` carries the keyword that failed (`required`, `type`, `oneOf`). Two missing properties of one object differ by their loci, so the discriminator does not repeat the property. The other rules yield at most one finding per field, and carry none. ^discriminator

**Region.** The region gives the line and the column at which the node of the field starts, read from the YAML node tree of the record and counted in Unicode code points. A finding on a field absent from the record takes the region of the closest existing ancestor of that field, where the absence is detected. A finding on the whole record, or on an absent field whose closest existing ancestor is the whole record, has no region. ^region

**Rules.** The driver describes every rule of the check, with its summary and its severity as default level, whether or not the run reports a finding of that rule. ^rules

**Completeness.** A record that cannot be read, or that fails `schema-conformance`, is checked by no other rule, since those rules read the record through the layout of its schema. A run that holds such a record is therefore incomplete. It declares one invocation whose `executionSuccessful` is `false`, with one notification of level `error` per such record, naming the record and the skipped rules. A run that applies every rule to every record writes no invocation, which the profile leaves optional. ^completeness

**Output path.** The option `--output PATH` writes the log to a file, creating its missing parent directories, in place of the standard output. It is valid with `--format sarif` only, and is otherwise refused with the exit code 2 of a usage error. A log that cannot be written ends the command with the exit code 2, outside the exit statuses that a consumer declares, so the gate reports the check as failed. ^output

## Constraints that decide the form

- **The default output is used until 2026-11-06.** The poster of Mixture-Input Encoding runs `ekthesis check` in its default form. Therefore, the text lines and the exit codes stay unchanged, and SARIF is an option.
- **The identity omits the message, the level and the line.** A discriminator must therefore name stable offending content. The message of a validation error belongs to the `jsonschema` library and may change with its version, so the discriminator takes the keyword instead.
- **The gate alone writes `fingerprints` and `suppressions`.** The profile marks both as *gate only*, so the log holds neither, not even an empty `suppressions` array.
- **The gate runs each check without a shell.** It reads the log from a path that the consumer declares, so the producer must write to a named file without a redirection.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| Discriminator written only when two results of one rule share a locus in the log | Fewer discriminators | The identity of a finding would change when another finding at its field is repaired |
| The message of a validation error as discriminator | Separates every pair of errors | The wording belongs to the validator, and a new version of `jsonschema` would rename the findings |
| The field path parsed back from its printed form | No change to the type of a finding | The printed form does not quote every key that the syntax of Ekphrasis quotes, so a key holding `"` or `]` does not parse back |
| Resource `path:` whenever the record breaks its schema | A single rule, independent of the validity | The resource of a record would change whenever an unrelated error appears or disappears |
| A root found from the enclosing Git repository | No dependence on the working directory | A record outside any repository would have no root, and a submodule would make the root ambiguous |
| The object that lacks a required property as locus, with the property in the discriminator | The locus names a node of the record | The profile gives a missing field the pointer of that field as locus, and the region of its closest existing ancestor |
| A run declared complete when a record fails its schema | The run matches the exit code, which a schema error already makes non-zero | The other rules were not applied to that record, and the profile requires a run that skips rules to declare a failed invocation |
| A successful invocation written on every complete run | Every log states its completeness | The profile leaves it optional, and the absence of a failed invocation already declares a complete run |

## Consequences

- **Renamed records.** A record that starts declaring its identifier, or whose identifier changes, changes resource. The gate maps the old resource onto the new one through its declared map of resources.
- **Positions.** An insertion above a sequence item renames the findings below it, since the locus holds the position of the item. The migration plan of Elenchos records the same limitation for the list indices of other producers.
- **Identities of missing properties.** A missing required property moved from the locus of its object, with the discriminator `required:<property>`, to the pointer of the property, with the discriminator `required`. A suppression written against the former identity matches no result. The gate counts it as unverified while the run of `ekthesis` is incomplete, which a missing property always makes it, and reports it as stale once the run is complete.
- **Incomplete runs at the gate.** The gate reports a run that skips rules as a result `check/incomplete`, and leaves unverified the suppressions of `ekthesis` that the run does not match. A record that fails its schema already yields a blocking error, so the verdict of the gate changes only by that added result.
- **Printed field paths.** The printed field path of a text line does not quote every key that the syntax of Ekphrasis quotes. Aligning it would change the default output, so the alignment waits until the poster no longer reads that output.
