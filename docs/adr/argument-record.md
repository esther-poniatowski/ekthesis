---
tags:
  - decision
status: accepted
created: 2026-10-31
revised: 2026-11-14
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Argument record and its check
---
# Argument record and its check

> [!WARNING] Amended
> On 2026-11-02, the decision of `geonexus` on [designation and typography](https://github.com/esther-poniatowski/geonexus/blob/584a14f134e7b6231eeae31518622439acf10d00/docs/_decisions/designation-and-typography.md) divides an exposition into an argument, valid for any audience, and a projection of that argument for one audience and one venue. The audience, the glossary and the notation of a projection are bound by keys that Anagraphe resolves, instead of links in the record.

> [!QUESTION] Goal: which form do the record of an exposition, its registries and its check take, where the [decision on the provenance of ideas](provenance-of-ideas.md) leaves the form open?

The decision on the provenance of ideas fixes three contents that an exposition must express: the provenance of each idea, whether the exposition is bound to its sources, and the requirements on each relation. `ekthesis` implements these rules in the contract `ekthesis:exposition@3`, two closed registries and the command `ekthesis check`. The first consumer is a poster of a research project. This revision of 2026-11-11 applies the decision of `geonexus` on [independent research and exposition](https://github.com/esther-poniatowski/geonexus/blob/269af033895ef4258724dfc779086d32826be631/docs/_decisions/independent-research-and-exposition.md), which retires the research export: a referenced idea states the kind of its unit, no rule reads a unit through an export, and a relation between two referenced ideas is unverified.

## Decision

**Record.** One record describes one exposition. The record holds four groups of fields:

- the identity of the exposition;
- its ideas;
- its relations;
- its parts, in reading order.

Each part lists its ideas in order, and one idea may appear in several parts. The audience and the glossary are named by links, since the schema takes no `$ref` into another repository. The venue constraints are named by a logical target of a constraints record, or by the link to a note of constraints that the field held before, as the [decision on venue constraints](constraints.md#^constraints-names) states. ^record

**Referenced idea.** A referenced idea names the record or the unit that states it by a logical target of Anagraphe, under its [ADR 0006](https://github.com/esther-poniatowski/anagraphe/blob/main/docs/adr/0006-logical-targets.md): a mapping `{repository, id, unit}`, whose repository is omitted inside the repository of the record. A note is named by the `id` of its frontmatter, and a unit of a note by its block anchor without the caret; a heading is not a unit. `ekthesis` validates the form of the target, and Anagraphe resolves it, so the existence of the record and of its unit is checked by `anagraphe targets check`, under the decision of `geonexus` on [cross-repository resolution](https://github.com/esther-poniatowski/geonexus/blob/95f893d9719604ae7a0fcca2b4c899944b47991b/docs/_decisions/cross-repository-record-resolution.md#canonical-reference). The retained version 1 names its unit by a relative Markdown link, which the check resolves from the directory of the record. No rule reads a unit through an export. ^referenced-idea

**Kind of a referenced idea.** A referenced idea states the kind of its unit under `kind`, the field in which an authored idea states its own kind. An idea that holds a link under `source` is referenced, and an idea that holds none is authored. The kind of a referenced idea is required, for two reasons. First, the decision of `geonexus` requires an exposition to state the kind of each referenced idea. Second, under the [versioning rule of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/5750ad7fd0f95a7670f8a24953a7dbd990f98e66/docs/_decisions/tool-roles.md#shared-conventions), a field made required later takes a new version of the contract, whereas a requirement relaxed later keeps the version. The kind is an identifier in lower kebab-case, such as `claim` or `definition`, and no registry of `ekthesis` closes its values, since the kinds of a unit belong to its source. No rule reads that kind yet: the rule `relation-requirements` reads only whether an idea is authored, and names the stated kind in its message. The closed list of the kinds of a referenced idea waits for the first rule that reads them, such as a check of the order of the moves of a part. The stated kind may diverge from the kind recorded by the source, and no check reports the divergence, as the decision of `geonexus` accepts. ^referenced-kind

**Roles of the fields.** Annotations of the schema state which field holds each identifier, reference, registry value, source link and binding to the sources. Therefore, the check names no field of a record:

- `x-identifier` at the root names the identifier of the record, as Ekphrasis reads it; on a definition reached as the items of a sequence, it names the identifier of each item;
- `x-refers` names the definition whose items a field identifies;
- `x-registry` names the registry that holds the values of a field; declared inside a branch of a `oneOf` or an `anyOf`, it applies only to an item that satisfies that branch, so the registry of authored kinds binds the kind of an authored idea only;
- `x-resolves: file` marks a link to the source of an idea, in the retained version 1;
- `x-role` marks the field stating whether the exposition is bound to its sources, and the source and the target of a relation. ^field-roles

**Registries.** Each registry is a data file of the package, and the schema leaves its values unenumerated. Therefore, each registry is the single source of its values, and its membership is checked by a rule of its own. The registry of relations holds the 23 relations of Rhetorical Structure Theory, divided into 16 subject-matter relations and 7 presentational relations [mann1988]. ^registries

**Required classes.** Each subject-matter relation requires a recorded relation of the class named after it. Among the presentational relations, an evidence requires a support and an antithesis requires an incompatibility. Every other presentational relation requires no class. The registry of relations is the only source of these classes: each source records its relations in its own vocabulary, which `ekthesis` does not read. ^required-classes

**Forms of an elaboration.** Rhetorical Structure Theory lists six forms of an elaboration: set and member, abstraction and instance, whole and part, process and step, object and attribute, generalization and specific [mann1988]. An elaboration between two referenced ideas states its form. An illustration takes the form abstraction and instance, and that form requires a recorded instance. Every other form requires the class named after the elaboration. ^elaboration-forms

**Direction.** In a mononuclear relation, the source is the satellite and the target is the nucleus. In a multinuclear relation, the source and the target are two nuclei, in reading order. ^direction

**Admitted forms as data.** The two forms of the [admitted relations with an authored idea](provenance-of-ideas.md#^authored-relations) are read from the registries:

- the first form holds for every presentational relation that requires no class, whichever of its two ideas is authored;
- the second form holds when the source is an authored idea of a kind listed by the relation under `admitted-authored-sources`, and the target is referenced. The elaboration admits an illustration. ^admitted-forms

A [synthesis](provenance-of-ideas.md#^syntheses) adds no idea. Its part lists again the referenced ideas reformulated by the synthesis. Therefore, the restatement and the summary list no authored kind.

**Severities and order.** The check applies the rules on the provenance of ideas only to a record that conforms to its schema. These rules read the fields of the record through the annotations of the schema. The check reports each relation that requires a class between two referenced ideas as unverified, at the severity of a warning, since `ekthesis` reads no source that records the relation. Every other finding is an error. ^severities

## Constraints that decide the form

- **Kleisis delivers owned contracts only within their source.** When a contract references a schema of another repository, its closure fails. Therefore, the record names its audience, glossary and venue by links.
- **`ekthesis` reads no source.** Under the decision of `geonexus` on [independent research and exposition](https://github.com/esther-poniatowski/geonexus/blob/269af033895ef4258724dfc779086d32826be631/docs/_decisions/independent-research-and-exposition.md), no export carries the units of a source or their relations. Therefore, the record states the kind of each referenced idea, and the check reads no recorded relation.
- **Anagraphe has not yet published the form of a logical target.** Therefore, a referenced idea names its unit by a link, which the check resolves, until a logical target replaces the link.
- **The schema is edited in Ekphrasis, and read by the check.** Ekphrasis ignores every keyword prefixed by `x-` beyond its own. Therefore, the annotations of the check stay in the schema without affecting the form of a record.
- **A rule must fail alone on its planted record.** A registry enumerated in the schema would fail the schema rule together with the registry rule. Therefore, the values of a registry stay outside the schema.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| Field names written in the code of the check | Shorter code | A renamed field breaks the check silently, and the schema is no longer the single source of the form of a record |
| Registries enumerated in the schema | A dropdown in the form of Ekphrasis | Two sources of each value; the schema rule and the registry rule fail together |
| The two admitted forms written as conditions in the code | No field `admitted-authored-sources` | The forms change with the registry, and a condition naming a relation duplicates its entry |
| A remote link admitted as a source | A unit of another repository can be cited | No anchor can be checked; a logical target serves that case once Anagraphe publishes its form |
| A unit named by its identifier in an export that the record names | The check verifies that the unit exists, and that the export records each relation between two units | The decision of `geonexus` on independent research and exposition retires the export; the existence of a cited unit moves to the resolution of logical targets by Anagraphe |
| The kind of a referenced idea optional | No record changes before a rule reads the kind | The decision of `geonexus` requires each referenced idea to state its kind, and a field made required later takes a new version of the contract |
| A closed registry of the kinds of a referenced idea | Each stated kind is checked | The kinds of a unit belong to its source, and no rule reads them yet |
| A field other than `kind` for the kind of a referenced idea | Each field follows one registry, and the layout of the schema needs no branch | One property of an idea would take two names, one for each provenance |
| An illustration between referenced ideas requires any recorded elaboration | No form on a relation | A recorded relation of a whole and its part would license presenting one unit as an instance of the other |
| A relation `illustration` added to the registry of relations | A record states no form | The registry holds the relations of Rhetorical Structure Theory, which counts an illustration as a form of the elaboration, so a second relation would duplicate the elaboration |

## Consequences

- **Sources.** The check reads no source. It resolves each link to a source, and reports each relation between two referenced ideas that requires a class as unverified. The rules `export-conformance`, `existing-units` and `recorded-relations`, which read the exports, are removed with the [contract of a research export](export-contract.md).
- **Version.** The contract `ekthesis:exposition@3` drops the fields `exports` and `unit` of version 1, requires the kind of every idea, and names the source of a referenced idea by a logical target. Version 2, which kept the link, was retired before any release, since no record followed it. Under the [versioning rule of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/5750ad7fd0f95a7670f8a24953a7dbd990f98e66/docs/_decisions/tool-roles.md#shared-conventions), version 1 stays in the registry of schemas until every record has migrated, and the check applies the same rules to its records. A record of version 1 migrates by naming version 3, stating the kind of each referenced idea, and writing its source as a logical target; each note that it cites then declares `id` in its frontmatter.
- **Classes.** The registry of relations names the class that each relation requires, and no source declares those classes.
- **Syntheses.** The decision on the provenance of ideas treats a synthesis as a device that adds no idea, rather than as an authored idea. Therefore, the check reports an authored source of a restatement or a summary as an error, and the registry of authored kinds keeps its four kinds.
- **Forms.** The registry of relations lists the forms of the elaboration, each with the class that it requires, and the schema gains a field naming the form of a relation whose entry lists forms. Until that change, the check reads every elaboration as requiring the class named after it.
- **Judgment.** No rule judges whether an authored idea carries content about the subject of the exposition. The author and the reviewer judge it, as the decision on the provenance of ideas states.
- **Modularity.** The parts of a record are generic: they name no feature of one kind of artifact. A field specific to one kind, such as the panels of a poster or the frames of a slide deck, enters a contract of its own, which extends a common core holding the identity, the ideas, the relations and the parts. That split requires the layout of the check to follow a `$ref` into another schema file of the package.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ○ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the classification of the relations into subject-matter and presentational
