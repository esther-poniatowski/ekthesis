---
tags:
  - proposal
index: "[Proposals](docs/proposals/_index.md)"
aliases:
  - Proposals for the exposition family
---
# Proposals for the exposition family

The goal [`exposition-family`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L76), carried from `gnomon`, specifies the records of an exposition. The [argument record](../adr/argument-record.md) fixes their first form.

## Illustration by an existing case

An illustration presents a case as an instance of a concept. Under the [provenance of ideas](../adr/provenance-of-ideas.md#^provenance), the case is either authored for the reader, or referenced from a source that already records it. The candidate covers the referenced case. Between two referenced ideas, an illustration is an elaboration, a subject-matter relation, so the export must record a relation of the class required by an elaboration. Rhetorical Structure Theory counts the pair of an abstraction and its instance among the forms of an elaboration, beside the pairs of a whole and its part or of a process and its step.

`gnomon` records the relation from a case to a concept or an answer as `exemplifies`, whose use takes one of five values. Four uses stay in `gnomon`, since each tests or establishes a claim: `witness`, `counterexample`, `boundary-case` and `construction`. The use `instance` serves an illustration. The decision of `gnomon` on its scope moves that use to `ekthesis`, but an illustration by a referenced case then finds no recorded relation behind it. Therefore, the candidate keeps `instance` as a relation that `gnomon` records and exports, and maps it onto the class required by an elaboration in the contract of the export. A variant divides that class by the forms of an elaboration, so that an illustration requires a recorded instance rather than any recorded elaboration. The relation `exemplifies`, rather than a record kind, carries the example, since an example is a role played by a case relative to a target.

**Literature.** Rhetorical Structure Theory, for the forms of an elaboration.

**Bears on.** [`exposition-family`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L76), and the [classes required by rhetorical relations](../adr/argument-record.md#^required-classes), still provisional.

**Retired source.** `docs/design/_backup/object-types-ontology/obj-example.md` and `docs/design/_backup/object-types-ontology/obj-counterexample.md` of `gnomon`, at commit 9e138e2.
