---
tags:
  - decision
status: proposed
created: 2026-10-31
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Provenance of ideas and relations
---
# Provenance of ideas and relations

> [!QUESTION] Goal: on what may each idea and each relation of an exposition rest, and what must the source of its ideas record for the exposition to present them?

An exposition, such as an article, a talk, a course or a poster, presents ideas to an audience and relates them. Its ideas come from research, from teaching, from documentation or from the author alone. Under the earlier rule of `gnomon`, an exposition added no content. That rule required a research unit for every example and every motivation. The [decision of `gnomon` on its scope](https://github.com/esther-poniatowski/gnomon/blob/main/docs/adr/research-scope.md) moves exposition to `ekthesis` and replaces that rule by a rule of provenance, stated below.

## Decision

Each idea of an exposition takes one of two forms:

- a **referenced idea** names a unit of an external source by its identifier, and reads its kind and its statement through the contract of the export of that source;
- an **authored idea** is written by the author, and declares one kind among four: illustration, analogy, motivation, and premise granted by the audience. ^provenance

An exposition declares whether it presents research. In an exposition that presents research, each idea that carries content about the objects of the inquiry references a research unit. An idea carries content about an object when it could be true or false of that object. Therefore, an authored idea of such an exposition carries content about other objects only. For instance, an illustration may describe a familiar situation, an analogy its source domain, and a motivation the practice of the audience. ^research-artifacts

Each relation of an exposition is a relation of Rhetorical Structure Theory. That theory divides its relations into two kinds [mann1988]. A subject-matter relation, such as a cause, a condition or a contrast, relates the contents of two units, and its intended effect is that the reader recognizes that relation. A presentational relation, such as a motivation, a background or a concession, aims to increase an inclination of the reader, such as belief or the ability to understand.

When both units of a relation are referenced, the relation requires the following from the export:

- a subject-matter relation requires a recorded relation of the same class;
- a presentational relation requires no recorded relation, with two exceptions, since the effect of each rests on a relation between the contents:
    - an evidence presents one unit as support for a claim, and requires a recorded support;
    - an antithesis presents two units as incompatible, so that the reader favours one of them, and requires a recorded incompatibility. ^relation-requirements

In an exposition that presents research, a relation with an authored idea is admitted in three forms only:

- a presentational relation other than an evidence and an antithesis, since an authored idea may help the reader understand, accept or want to read a research unit, but cannot add a warrant to it;
- the instance relation of an illustration, an elaboration in Rhetorical Structure Theory, which presents an authored case as an instance of a referenced concept;
- a restatement or a summary, realized by a synthesis: it reformulates referenced units and adds no idea. ^authored-relations

## Constraints that decide the rule

- **The ideas of an argument come from any activity.** A course or a piece of documentation has no research records behind its examples. Therefore, `ekthesis` cannot require a record for every idea.
- **The warrant of a research claim is fixed by its grounds.** A claim of an inquiry is established by the grounds and the assessment recorded in research, and these do not depend on the reader. Therefore, an exposition that presents research may not add a claim about the objects of the inquiry, nor present an authored idea as evidence for a research claim.
- **A presentational relation asserts no relation between the contents, except through support or incompatibility.** A background, an enablement or a motivation aims at the understanding or the desire of the reader, so it holds independently of the relations recorded by the source. An evidence and an antithesis aim at belief and at positive regard, but each produces its effect through a relation between the contents.
- **`ekthesis` reads only the contract of an export.** The contract of the export names units, symbols and relations with their classes, so every requirement above is checked from the entries of the contract. A check needing the internal fields of a source binds `ekthesis` to that source, and belongs to the consumer that uses both.
- **An authored premise about the objects of an inquiry would be an unrecorded claim.** In the theory of argumentation, a speaker may start from a premise because the audience grants it [perelman1958]. Within an exposition that presents research, a premise about the objects of the inquiry is a claim about those objects. Therefore, that premise must be recorded as a research unit first. A premise about other matters, such as the practice of the audience, stays authored.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| An exposition adds no content, as `gnomon` required | Every idea has a canonical record | An exposition with no research behind it has no records to cite, and research records must then hold motivations and examples serving a reader only |
| Any idea and any relation are admitted | An author writes freely | Then, an exposition of research may hold claims and warrants absent from every research record |
| Every relation requires a recorded relation | One rule for all relations | A background or a motivation asserts no relation between the contents, so the rule demands records for relations that the exposition does not assert |
| Provenance by reference or by declared kind, with the requirements of Rhetorical Structure Theory | Each idea and each relation states its basis, and the requirement for research applies only to expositions that present research | The kinds of authored idea, and the classes of relation in the contract, must be maintained as closed registries |

The present decision takes the last option.

## Consequences

- The schema of an idea admits either a reference by identifier or an authored kind drawn from a closed registry of four kinds.
- The registry of rhetorical relations states, for each relation, its kind in Rhetorical Structure Theory and, if any, the class of the contract required by that relation.
- A check verifies each reference against the export, each declared kind against its registry, and each relation against [the requirements of a relation on the export](#^relation-requirements) and [the admitted forms of a relation with an authored idea](#^authored-relations). The author and the reviewer judge whether an authored idea carries content about the objects of the inquiry. No check computes that judgment.
- The note on [exposition](../theory/exposition.md) is rewritten under the present rule. Its reading of Rhetorical Structure Theory changes: that note matches `supports` to a subject-matter connector, whereas an evidence is a presentational relation that requires a recorded support.
- The renaming of a symbol for a venue, the glossaries and the audiences are settled by later decisions of `ekthesis`.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); subject-matter and presentational relations
- [perelman1958] ◐ Perelman & Olbrechts-Tyteca, *La nouvelle rhétorique : traité de l'argumentation*, Presses Universitaires de France, 1958; translated by Wilkinson & Weaver as *The New Rhetoric: A Treatise on Argumentation*, University of Notre Dame Press, 1969; argumentation relative to its audience, §§1–4 and Part Two, checked through [Hitchcock's discussion notes](https://humanities.mcmaster.ca/~hitchckd/perelmandiscussion.htm)
