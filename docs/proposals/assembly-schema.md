---
tags:
  - proposal
index: "[Proposals](docs/proposals/_index.md)"
aliases:
  - Proposals for the assembly schema
---
# Proposals for the assembly schema

The goal [`assembly-schema`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L79), carried from `gnomon`, divides between the two tools. `ekthesis` receives the status `core` or `elaboration` of a component of an argument, the views that expand chosen components, and the check of the core route. The gaps of an assembly, its limits of validity, its deferred components and the query of its weakest link stay in `gnomon`.

## Status relative to one argument

The status `core` or `elaboration` of an idea belongs to the record of one exposition, never to the source of the idea. A unit takes part in several arguments, and one argument may answer a question stated by no research record. Then, the same unit may be core in one argument and an elaboration in another. A status recorded on the unit would therefore let one argument stand for all of them. The expositions that present a unit, with the status of the unit in each, are found by a query over their records.

**Literature.** None cited.

**Bears on.** [`assembly-schema`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L79), and the [record of an exposition](../adr/argument-record.md#^record), still without a status.

**Retired source.** `docs/design/2-architecture/reasoning-structure.md`, `docs/design/_backup/arguments-reasoning/argument-bundles.md` and `docs/design/_backup/schema-fields-base.md` of `gnomon`, at commit 9e138e2.
