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

The [findings profile](https://github.com/esther-poniatowski/elenchos/blob/main/docs/profile.md) fixes the subset of SARIF 2.1.0 that a producer writes, and the identity `tool|ruleId|resource|locus|discriminator` that the gate builds from it. The option `ekthesis check --format sarif` writes that log. Four inputs of the identity depend on choices of the producer: the root of the paths, the resource, the discriminator and the region.

## Decision

**Root.** The working directory stands for the root `SRCROOT` of the repository. Each artifact URI and each resource `path:` is the path of the record relative to that directory. A record outside the working directory has no such path, so the command refuses it with the exit code 2 of a usage error, before checking any record. ^root

**Resource.** The resource is `id:<identifier>` when three conditions hold:

- the record names a known contract;
- the schema of that contract declares `x-identifier` at its root;
- the record holds a non-empty text in the declared field.

Otherwise the resource is `path:<path>`. The identifier is read even when the record breaks its schema elsewhere. Therefore, an error in another field leaves the resource of the record unchanged. ^resource

**Locus.** The locus is the JSON Pointer of the field of the finding, converted from its segments, so that a key holding `.`, `/` or `~` converts exactly. A finding on the whole record has the empty locus. ^locus

**Discriminator.** The rule decides whether its findings carry a discriminator, independently of the other findings of the log. Every finding of `schema-conformance` carries the keyword that failed, followed for `required` by the missing property (`required:statement`). The other rules yield at most one finding per field, and carry none. ^discriminator

**Region.** The region gives the line and the column at which the node of the field starts, read from the YAML node tree of the record and counted in Unicode code points. A finding on the whole record, or on a field absent from the record, has no region. ^region

**Rules.** The driver describes every rule of the check, with its summary and its severity as default level, whether or not the run reports a finding of that rule. ^rules

## Constraints that decide the form

- **The default output is used until 2026-11-06.** The poster of Mixture-Input Encoding runs `ekthesis check` in its default form. Therefore, the text lines and the exit codes stay unchanged, and SARIF is an option.
- **The identity omits the message, the level and the line.** A discriminator must therefore name stable offending content. The message of a validation error belongs to the `jsonschema` library and may change with its version, so the discriminator takes the keyword instead.
- **The gate alone writes `fingerprints` and `suppressions`.** The profile marks both as *gate only*, so the log holds neither, not even an empty `suppressions` array.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| Discriminator written only when two results of one rule share a locus in the log | Fewer discriminators | The identity of a finding would change when another finding at its field is repaired |
| The message of a validation error as discriminator | Separates every pair of errors | The wording belongs to the validator, and a new version of `jsonschema` would rename the findings |
| The field path parsed back from its printed form | No change to the type of a finding | The printed form does not quote every key that the syntax of Ekphrasis quotes, so a key holding `"` or `]` does not parse back |
| Resource `path:` whenever the record breaks its schema | A single rule, independent of the validity | The resource of a record would change whenever an unrelated error appears or disappears |
| A root found from the enclosing Git repository | No dependence on the working directory | A record outside any repository would have no root, and a submodule would make the root ambiguous |

## Consequences

- **Renamed records.** A record that starts declaring its identifier, or whose identifier changes, changes resource. The gate maps the old resource onto the new one through its declared map of resources.
- **Positions.** An insertion above a sequence item renames the findings below it, since the locus holds the position of the item. The migration plan of Elenchos records the same limitation for the list indices of other producers.
- **Printed field paths.** The printed field path of a text line does not quote every key that the syntax of Ekphrasis quotes. Aligning it would change the default output, so the alignment waits until the poster no longer reads that output.
