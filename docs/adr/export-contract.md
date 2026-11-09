---
tags:
  - decision
status: accepted
created: 2026-11-09
revised: 2026-11-09
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Contract of a research export
---
# Contract of a research export

> [!QUESTION] Goal: which units and which relations does a source publish in its export, in which form, and which classes may an exposition read from it?

The [decision on the provenance of ideas](provenance-of-ideas.md#^provenance) lets a referenced idea read its kind and its statement through the contract of the export of its source. The [argument record](argument-record.md#^required-classes) names the classes that a relation between two referenced ideas requires, and treats them as provisional until a source publishes its relations. `gnomon`, the first source, now generates an export, so the contract fixes the form of that export. The [exposition pilot](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/exposition-pilot-profile.md) has not yet settled the status of a presented unit or the trace of its conditions. Therefore, this first version of the contract publishes only the fields that the checks of `ekthesis` can already read.

## Decision

`ekthesis` owns and publishes the contract `ekthesis:export@1`, in the schema `export.schema.yaml` of its package, and exports it through `kleisis`. A source declares a dependency on that contract and imports no code of `ekthesis`. The source generates its export, commits it, and never edits it by hand. ^export-owner

**Units.** Each unit of the export carries its dotted identifier, the record that holds it, and the segments of the unit inside that record. It also carries its kind, the kind of its record in the source, its statement, its status, and the units that supersede it. The identifier of a unit stays fixed while the unit keeps its content, so an exposition pins an export by the commit of its source. The kind is an opaque label in this version, since no check of `ekthesis` reads it yet. ^export-units

**Relations.** Each relation carries an identifier, unique in the export. An argument then cites the relation instead of restating it, as the [decision of `geonexus` on designation and typography](https://github.com/esther-poniatowski/geonexus/blob/584a14f134e7b6231eeae31518622439acf10d00/docs/_decisions/designation-and-typography.md) requires. A relation names either a source and a target, or the members of a set. Both ends of every relation, and every member of a set, are units of the same export. The name of the relation and its use in the source are carried for provenance, and stay opaque to the reader. ^export-relations

**Classes.** The contract enumerates the classes that a source can publish: ^export-classes

- `support`, from the supporting unit to the supported one, which an evidence requires;
- `condition`, from the condition to the unit that holds under it;
- `incompatibility`, which an antithesis requires;
- `contrast`, between two units that differ in a stated respect;
- `elaboration`, from the unit that adds detail to the unit that it details, with its form;
- `solutionhood`, from a question to a unit that answers it;
- `instance`, from an instance to the abstraction that it instantiates.

A subject-matter relation whose class is not in this list remains reported as unverified, at the severity of a warning, as the [severities of the check](argument-record.md#^severities) state.

**Forms of an elaboration.** A form is no class. An elaboration in the export states one of five forms: set and member, whole and part, process and step, object and attribute, generalization and specific. The sixth form of Rhetorical Structure Theory, abstraction and instance, is the class `instance`, as the [forms of an elaboration](argument-record.md#^elaboration-forms) require for an illustration. ^export-forms

**Symmetric and set relations.** An incompatibility and a contrast are symmetric. An antithesis between two referenced ideas is licensed by an incompatibility between their two units in either direction, since the nucleus of the antithesis is a choice of presentation. An incompatible set of more than two members holds of the whole set and of none of its pairs, so it licenses no antithesis between two of its members. ^export-symmetry

**Overridden findings.** An export records whether its source generated it while its own check reported an error, so that a reader tells such an export from a clean one. ^export-findings

**Deferred to a later version.** Four questions wait for evidence that the first version lacks:

- the closed list of the kinds of a unit, which a rule of `ekthesis` must first read;
- the status of a presented unit, such as an entertained or a superseded claim, and the conditions of each unit for the check of traces, which the exposition pilot settles;
- the subject-matter classes without a source, such as a cause or an evaluation, which require a decision on whether a relation stated inside a claim licenses them;
- the logical target of a referenced idea, whose form Anagraphe publishes, and which replaces the relative link of the [referenced idea](argument-record.md#^referenced-idea).

A source publishes no symbol and no formula in this version, since no rule of `ekthesis` reads them, and the printed form of a symbol belongs to Onomasia. ^export-deferred

## Constraints that decide the contract

- **A field that no check reads is dead data.** The contract carries only the fields that a check of `ekthesis` reads now, and the fields that the identity of a unit or a relation requires.
- **`ekthesis` reads classes, never the vocabulary of a source.** The names of the relations of a source stay opaque, so that `ekthesis` accepts sources other than `gnomon`.
- **The export is generated.** The schema serves validation and display, not editing. Therefore, it enumerates its classes, whereas the registries of an exposition stay unenumerated, as the [argument record](argument-record.md#^registries) requires for edited records.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| A contract owned by `gnomon` | No dependency of the source on `ekthesis` | `ekthesis` reads ideas from sources other than research, so the reader states the contract |
| Every subject-matter class in the first version | One version for every source | No source fills them, and a class enumerated without a source invites a guessed mapping |
| Each form of an elaboration as a class | One field per relation | The argument record already reads an elaboration with a form, and only an instance has a recorded relation of its own |
| An incompatible set split into its pairs | Every antithesis checked against pairs | A minimal incompatible set of three has compatible pairs, so the split would assert false incompatibilities |
| Symbols and formulas in the export | A renamer reads the symbols of a source | No rule of `ekthesis` reads them, and a formula in the syntax of its source needs the parser of that source |
| A closed list of unit kinds now | The kind of a referenced idea is checked | No rule reads the kind yet, and the exposition pilot still revises its kinds |

## Consequences

- The schema `export.schema.yaml` joins the contracts that `ekthesis` exports through `kleisis`.
- The classes required by the [registry of relations](../../src/ekthesis/data/registries/relations.yml) keep their names; a later rule of the check reads the class of each recorded relation from the export, and resolves each warning on a required class against it.
- A source that depends on the contract validates its export against the materialized schema in its own tests.
