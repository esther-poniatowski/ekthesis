---
tags:
  - decision
status: accepted
created: 2026-10-31
revised: 2026-11-01
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Argument record and its check
---
# Argument record and its check

> [!WARNING] Amended
> On 2026-11-02, the decision of `geonexus` on [designation and typography](https://github.com/esther-poniatowski/geonexus/blob/584a14f134e7b6231eeae31518622439acf10d00/docs/_decisions/designation-and-typography.md) divides an exposition into an argument, valid for any audience, and a projection of that argument for one audience and one venue. The audience, the glossary and the notation of a projection are bound by keys that Anagraphe resolves, instead of links in the record.

> [!QUESTION] Goal: which form do the record of an exposition, its registries and its check take, where the [decision on the provenance of ideas](provenance-of-ideas.md) leaves the form open?

The decision on the provenance of ideas fixes three contents that an exposition must express: the provenance of each idea, whether the exposition is bound to its sources, and the requirements on each relation. The first version of `ekthesis` implements these rules in the contract `ekthesis:exposition@1`, two closed registries and the command `ekthesis check`. The first consumer is a poster of a research project, and the sources of that project publish no export yet.

## Decision

**Record.** One record describes one exposition. The record holds four groups of fields:

- the identity of the exposition;
- its ideas;
- its relations;
- its parts, in reading order.

Each part lists its ideas in order, and one idea may appear in several parts. The audience, the glossary and the venue constraints are named by links, since the schema takes no `$ref` into another repository. ^record

**Referenced idea.** A referenced idea names its unit by a relative Markdown link to the file that states it, with an optional anchor of a block (`#^id`) or of a heading. The check resolves the link from the directory of the record. A link to a remote address is rejected, since no remote file can be checked for its anchor. When the source of an idea publishes an export, the idea names its unit instead, by the identifier of the unit under `unit`, and the record names that export under `exports`, by a relative link that the check resolves as it resolves a link to a source. An idea takes one of the two forms, never both. ^referenced-idea

**Roles of the fields.** Annotations of the schema state which field holds each identifier, reference, registry value, source link and binding to the sources. Therefore, the check names no field of a record:

- `x-identifier` at the root names the identifier of the record, as Ekphrasis reads it; on a definition reached as the items of a sequence, it names the identifier of each item;
- `x-refers` names the definition whose items a field identifies;
- `x-registry` names the registry that holds the values of a field;
- `x-resolves: file` marks a link to the source of an idea;
- `x-role` marks the field stating whether the exposition is bound to its sources, and the source and the target of a relation. ^field-roles

**Registries.** Each registry is a data file of the package, and the schema leaves its values unenumerated. Therefore, each registry is the single source of its values, and its membership is checked by a rule of its own. The registry of relations holds the 23 relations of Rhetorical Structure Theory, divided into 16 subject-matter relations and 7 presentational relations [mann1988]. ^registries

**Required classes.** Each subject-matter relation requires a recorded relation of the class named after it. Among the presentational relations, an evidence requires a support and an antithesis requires an incompatibility. Every other presentational relation requires no class. A class named after a relation is provisional: no source publishes the classes of its relations yet. ^required-classes

**Forms of an elaboration.** Rhetorical Structure Theory lists six forms of an elaboration: set and member, abstraction and instance, whole and part, process and step, object and attribute, generalization and specific [mann1988]. An elaboration between two referenced ideas states its form. An illustration takes the form abstraction and instance, and that form requires a recorded instance. `gnomon` records an instance as the use `instance` of its relation `exemplifies`, and maps that use onto the class `instance` of the contract. Every other form requires the class named after the elaboration. ^elaboration-forms

**Direction.** In a mononuclear relation, the source is the satellite and the target is the nucleus. In a multinuclear relation, the source and the target are two nuclei, in reading order. ^direction

**Admitted forms as data.** The two forms of the [admitted relations with an authored idea](provenance-of-ideas.md#^authored-relations) are read from the registries:

- the first form holds for every presentational relation that requires no class, whichever of its two ideas is authored;
- the second form holds when the source is an authored idea of a kind listed by the relation under `admitted-authored-sources`, and the target is referenced. The elaboration admits an illustration. ^admitted-forms

A [synthesis](provenance-of-ideas.md#^syntheses) adds no idea. Its part lists again the referenced ideas reformulated by the synthesis. Therefore, the restatement and the summary list no authored kind.

**Severities and order.** The check applies the rules on the provenance of ideas only to a record that conforms to its schema. These rules read the fields of the record through the annotations of the schema. A relation that requires a class between two ideas naming units, when the contract of an export publishes that class, is an error unless an export that the record names records it. The check reports every other relation that requires a class between two referenced ideas as unverified, at the severity of a warning: an idea referenced by a link names no unit, and a class outside the contract has no source. Every other finding is an error. ^severities

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
| The two admitted forms written as conditions in the code | No field `admitted-authored-sources` | The forms change with the registry, and a condition naming a relation duplicates its entry |
| A remote link admitted as a source | A unit of another repository can be cited | No anchor can be checked; the logical identifier of an export serves that case later |
| An illustration between referenced ideas requires any recorded elaboration | No form on a relation | A recorded relation of a whole and its part would license presenting one unit as an instance of the other |
| A relation `illustration` added to the registry of relations | A record states no form | The registry holds the relations of Rhetorical Structure Theory, which counts an illustration as a form of the elaboration, so a second relation would duplicate the elaboration |

## Consequences

- **Exports.** An idea whose source publishes an export names its unit, and the rule `recorded-relations` verifies each relation between two such ideas against the export, under the [contract of a research export](export-contract.md). The rules `export-conformance` and `existing-units` check that each named export follows the contract and holds each named unit.
- **Classes.** The classes required by subject-matter relations are renamed after the classes that the contract of an export declares.
- **Syntheses.** The decision on the provenance of ideas treats a synthesis as a device that adds no idea, rather than as an authored idea. Therefore, the check reports an authored source of a restatement or a summary as an error, and the registry of authored kinds keeps its four kinds.
- **Forms.** The registry of relations lists the forms of the elaboration, each with the class that it requires, and the schema gains a field naming the form of a relation whose entry lists forms. Until that change, the check reads every elaboration as requiring the class named after it.
- **Judgment.** No rule judges whether an authored idea carries content about the subject of the exposition. The author and the reviewer judge it, as the decision on the provenance of ideas states.
- **Modularity.** The parts of a record are generic: they name no feature of one kind of artifact. A field specific to one kind, such as the panels of a poster or the frames of a slide deck, enters a contract of its own, which extends a common core holding the identity, the ideas, the relations and the parts. That split requires the layout of the check to follow a `$ref` into another schema file of the package.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ○ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the classification of the relations into subject-matter and presentational
