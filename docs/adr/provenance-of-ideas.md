---
tags:
  - decision
status: accepted
created: 2026-10-31
revised: 2026-11-11
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Provenance of ideas and relations
---
# Provenance of ideas and relations

> [!QUESTION] Goal: on what may each idea and each relation of an exposition rest, and what must the source of its ideas record for the exposition to present them?

An exposition, such as an article, a talk, a course or a poster, presents ideas to an audience and relates them. Its ideas come from research, from teaching, from documentation or from the author alone. Under the earlier rule of `gnomon`, an exposition added no content. That rule required a research unit for every example and every motivation. The [decision of `gnomon` on its scope](https://github.com/esther-poniatowski/gnomon/blob/45de45d9f362ffc6340cba3837cd44a46cd3b172/docs/adr/research-scope.md) moves exposition to `ekthesis` and replaces that rule by a rule of provenance, stated below.

The decision of `geonexus` on [independent research and exposition](https://github.com/esther-poniatowski/geonexus/blob/269af033895ef4258724dfc779086d32826be631/docs/_decisions/independent-research-and-exposition.md) retires the research export, through which a referenced idea read its kind and its statement, and the relations of its source. This revision of 2026-11-11 states the referenced idea without that export: the exposition states the kind of each referenced idea and the relations between its ideas itself, and the check reports a relation between two referenced ideas as unverified.

## Decision

Each idea of an exposition takes one of two forms:

- a **referenced idea** names a unit of an external source, and states the kind of that unit and its statement itself, without reading them from the source;
- an **authored idea** is written by the author, and declares one kind among four: illustration, analogy, motivation, and premise granted by the audience. ^provenance

An exposition declares whether it is bound to its sources. The subject of an exposition is the set of objects that its sources describe, such as the objects of an inquiry, the behaviour of a program or the content of a course. In a source-bound exposition, each idea that carries content about its subject references a unit of a source. An idea carries content about an object when it could be true or false of that object. Therefore, an authored idea of such an exposition carries content about other objects only. For instance, an illustration may describe a familiar situation, an analogy its source domain, and a motivation the practice of the audience. ^source-bound

Each relation of an exposition is a relation of Rhetorical Structure Theory. That theory divides its relations into two kinds [mann1988]. A subject-matter relation, such as a cause, a condition or a contrast, relates the contents of two units, and its intended effect is that the reader recognizes that relation. A presentational relation, such as a motivation, a background or a concession, aims to increase an inclination of the reader, such as belief or the ability to understand.

When both ideas of a relation are referenced, the relation requires the following relation between their units, recorded by the sources:

- a subject-matter relation requires a recorded relation of the same class;
- a presentational relation requires no recorded relation, with two exceptions, since the effect of each rests on a relation between the contents:
    - an evidence presents one unit as support for a claim, and requires a recorded support;
    - an antithesis presents two units as incompatible, so that the reader favours one of them, and requires a recorded incompatibility. ^relation-requirements

The author answers for these requirements. `ekthesis` reads no source, so it checks a relation between two referenced ideas only against its own registry of relations, which states the class that each relation requires, and reports each relation that requires a class as unverified. ^unverified-relations

In a source-bound exposition, a relation with an authored idea is admitted in two forms only:

- a presentational relation other than an evidence and an antithesis, since an authored idea may help the reader understand, accept or want to read a unit of a source, but cannot add a warrant to it;
- the instance relation of an illustration, an elaboration in Rhetorical Structure Theory, which presents an authored case as an instance of a referenced concept. ^authored-relations

A synthesis realizes a restatement or a summary. A synthesis reformulates referenced units, and adds no idea. Therefore, a synthesis is a device of the exposition, not an idea of it. The synthesis presents the same referenced ideas again, and the record of the exposition declares no relation for it. In a source-bound exposition, an authored idea in place of the synthesis would carry content about the subject of the exposition. The [rule on source-bound expositions](#^source-bound) excludes such an idea. ^syntheses

## Constraints that decide the rule

- **The ideas of an argument come from any activity.** A course or a piece of documentation has no research records behind its examples. Therefore, `ekthesis` cannot require a record for every idea.
- **The warrant of a claim of a source is fixed by that source.** A claim of an inquiry is established by its recorded grounds and assessment, and a claim of documentation by the behaviour that it documents; neither depends on the reader. Therefore, a source-bound exposition may not add a claim about its subject, nor present an authored idea as evidence for a claim of a source.
- **A presentational relation asserts no relation between the contents, except through support or incompatibility.** A background, an enablement or a motivation aims at the understanding or the desire of the reader, so it holds independently of the relations recorded by the source. An evidence and an antithesis aim at belief and at positive regard, but each produces its effect through a relation between the contents.
- **`ekthesis` reads no source.** Under the decision of `geonexus` on [independent research and exposition](https://github.com/esther-poniatowski/geonexus/blob/269af033895ef4258724dfc779086d32826be631/docs/_decisions/independent-research-and-exposition.md), each tool stays usable alone, and an exposition cites the records of its consumer by logical target. No export carries the kinds of the units of a source or their relations. Therefore, an exposition states the kind of each referenced idea itself, and a requirement on a relation between two referenced ideas binds the author, not the check.
- **An authored premise about the subject would be an unrecorded claim.** In the theory of argumentation, a speaker may start from a premise because the audience grants it [perelman1958]. Within a source-bound exposition, a premise about the subject of the exposition is a claim about that subject. Therefore, that premise must be recorded as a unit of a source first. A premise about other matters, such as the practice of the audience, stays authored.
- **A synthesis adds no idea.** A restatement presents its nucleus again at a comparable length, and a summary presents its nucleus again at a shorter length [mann1988]. Therefore, a synthesis realizing either relation changes the form of referenced units, not their content.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| An exposition adds no content, as `gnomon` required | Every idea has a canonical record | An exposition with no source behind it has no units to cite, and its sources must then hold motivations and examples serving a reader only |
| Any idea and any relation are admitted | An author writes freely | Then, a source-bound exposition may hold claims and warrants absent from every source |
| Every relation requires a recorded relation | One rule for all relations | A background or a motivation asserts no relation between the contents, so the rule demands records for relations that the exposition does not assert |
| A fifth authored kind, `synthesis`, exempted from the rule on content | Each synthesis is an idea of its own, related to the restated units | Then, an authored idea about the subject of the exposition becomes admitted, and no check can separate a faithful synthesis from an unrecorded claim; the synthesis also duplicates the restated ideas |
| Provenance by reference or by declared kind, with the requirements of Rhetorical Structure Theory | Each idea and each relation states its basis, and the requirement of a reference applies only to source-bound expositions | The kinds of authored idea, and the classes required by each relation, must be maintained as closed registries |
| The requirements on a relation between referenced ideas checked against an export of each source | A relation that its sources do not record is reported as an error | The decision of `geonexus` on [independent research and exposition](https://github.com/esther-poniatowski/geonexus/blob/269af033895ef4258724dfc779086d32826be631/docs/_decisions/independent-research-and-exposition.md) retires the export: a tool of research would depend on a contract of `ekthesis`, and every source would generate that contract |

The present decision takes the last option.

## Consequences

- The schema of an idea admits either a reference to a unit with the kind of that unit, or an authored kind drawn from a closed registry of four kinds. The schema of an exposition declares, in the field `source-bound`, whether the exposition is bound to its sources.
- The registry of rhetorical relations states, for each relation, its kind in Rhetorical Structure Theory and, if any, the class of the recorded relation that it requires.
- A check verifies each reference, each authored kind against its registry, and each relation with an authored idea against [the admitted forms of a relation with an authored idea](#^authored-relations). It reports each relation between two referenced ideas that requires a class as unverified, under [the requirements of a relation on the sources](#^relation-requirements). The author and the reviewer judge whether an authored idea carries content about the subject of the exposition, and whether the sources record each unverified relation. No check computes these judgments.
- The note on [exposition](../theory/exposition.md) states the concepts under the present rule, and reads an evidence as a presentational relation that requires a recorded support.
- The [renaming of a symbol for a venue](symbol-renaming.md), the [glossaries](glossaries.md) and the [audiences](audiences.md) are settled by later decisions of `ekthesis`.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); subject-matter and presentational relations
- [perelman1958] ◐ Perelman & Olbrechts-Tyteca, *La nouvelle rhétorique : traité de l'argumentation*, Presses Universitaires de France, 1958; translated by Wilkinson & Weaver as *The New Rhetoric: A Treatise on Argumentation*, University of Notre Dame Press, 1969; argumentation relative to its audience, §§1–4 and Part Two, checked through [Hitchcock's discussion notes](https://humanities.mcmaster.ca/~hitchckd/perelmandiscussion.htm)
