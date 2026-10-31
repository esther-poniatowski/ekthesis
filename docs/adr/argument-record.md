---
tags:
  - decision
status: proposed
created: 2026-10-31
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Argument record and its check
---
# Argument record and its check

> [!QUESTION] Goal: which form do the record of an exposition, its registries and its check take, where the [decision on the provenance of ideas](provenance-of-ideas.md) leaves the form open?

The decision on the provenance of ideas fixes three contents that an exposition must express: the provenance of each idea, whether the exposition presents research, and the requirements on each relation. The first version of `ekthesis` implements these rules in the contract `ekthesis:exposition@1`, two closed registries and the command `ekthesis check`. The first consumer is a poster of a research project, and the sources of that project publish no export yet.

## Decision

**Record.** One record describes one exposition. The record holds four groups of fields:

- the identity of the exposition;
- its ideas;
- its relations;
- its parts, in reading order.

Each part lists its ideas in order, and one idea may appear in several parts. The audience, the glossary and the venue constraints are named by links, since the schema takes no `$ref` into another repository. ^record

**Referenced idea.** A referenced idea names its unit by a relative Markdown link to the file that states it, with an optional anchor of a block (`#^id`) or of a heading. The check resolves the link from the directory of the record. A link to a remote address is rejected, since no remote file can be checked for its anchor. The logical identifier of a unit in an export replaces the link once a source publishes an export. ^referenced-idea

**Roles of the fields.** Annotations of the schema state which field holds each identifier, reference, registry value, source link and research flag. Therefore, the check names no field of a record:

- `x-identifier` at the root names the identifier of the record, as Ekphrasis reads it; on a definition reached as the items of a sequence, it names the identifier of each item;
- `x-refers` names the definition whose items a field identifies;
- `x-registry` names the registry that holds the values of a field;
- `x-resolves: file` marks a link to the source of an idea;
- `x-role` marks the field stating whether the exposition presents research, and the source and the target of a relation. ^field-roles

**Registries.** Each registry is a data file of the package, and the schema leaves its values unenumerated. Therefore, each registry is the single source of its values, and its membership is checked by a rule of its own. The registry of relations holds the 23 relations of Rhetorical Structure Theory, divided into 16 subject-matter relations and 7 presentational relations [mann1988]. ^registries

**Required classes.** Each subject-matter relation requires a recorded relation of the class named after it. Among the presentational relations, an evidence requires a support and an antithesis requires an incompatibility. Every other presentational relation requires no class. A class named after a relation is provisional: no source publishes the classes of its relations yet. ^required-classes

**Direction.** In a mononuclear relation, the source is the satellite and the target is the nucleus. In a multinuclear relation, the source and the target are two nuclei, in reading order. ^direction

**Admitted forms as data.** The three forms of the [admitted relations with an authored idea](provenance-of-ideas.md#^authored-relations) are read from the registries:

- the first form holds for every presentational relation that requires no class;
- the second and the third forms hold when the source is an authored idea of a kind listed by the relation under `admitted-authored-sources`, and the target is referenced. The elaboration admits an illustration. The restatement and the summary admit each of the four kinds. ^admitted-forms

**Severities and order.** The check applies the rules on the provenance of ideas only to a record that conforms to its schema. These rules read the fields of the record through the annotations of the schema. Until a source publishes its relations, the check reports each relation that requires a class between two referenced ideas as unverified, at the severity of a warning. Every other finding is an error. ^severities

## Constraints that decide the form

- **Kleisis delivers owned contracts only within their source.** When a contract references a schema of another repository, its closure fails. Therefore, the record names its audience, glossary and venue by links.
- **The sources of the first consumer publish no export.** Therefore, a referenced idea points at a file, and the check can read no recorded relation.
- **The schema is edited in Ekphrasis, and read by the check.** Ekphrasis ignores every keyword prefixed by `x-` beyond its own. Therefore, the annotations of the check stay in the schema without affecting the form of a record.
- **A rule must fail alone on its planted record.** A registry enumerated in the schema would fail the schema rule together with the registry rule. Therefore, the values of a registry stay outside the schema.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| Field names written in the code of the check | Shorter code | A renamed field breaks the check silently, and the schema is no longer the single source of the form of a record |
| Registries enumerated in the schema | A dropdown in the form of Ekphrasis | Two sources of each value; the schema rule and the registry rule fail together |
| The three admitted forms written as conditions in the code | No field `admitted-authored-sources` | The forms change with the registry, and a condition naming a relation duplicates its entry |
| A remote link admitted as a source | A unit of another repository can be cited | No anchor can be checked; the logical identifier of an export serves that case later |

## Consequences

- **Exports.** A source that publishes an export replaces the relative links of its units by logical identifiers. Then, a new rule reads the recorded relations, and resolves each warning on a required class against the export.
- **Classes.** The classes required by subject-matter relations are renamed after the classes that the contract of an export declares.
- **Syntheses.** A synthesis restates referenced units, as the third form requires, but none of the four authored kinds describes it. Until the decision on the provenance of ideas settles this gap, the restatement and the summary admit each of the four kinds. A fifth kind, `synthesis`, would close the gap, and requires a revision of that decision.
- **Judgment.** No rule judges whether an authored idea carries content about the objects of the inquiry. The author and the reviewer judge it, as the decision on the provenance of ideas states.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ○ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the classification of the relations into subject-matter and presentational
