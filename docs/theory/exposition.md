---
tags:
  - theory
index: "[Theory](docs/theory/_index.md)"
aliases:
  - Exposition
  - Audience of an exposition
---
# Exposition

> [!QUESTION] Goal: what is an exposition, on what do its ideas and its relations rest, and what does its audience change?

An **exposition**, such as an article, a talk, a course or a poster, presents ideas to a declared audience, in an order chosen for that audience, and relates them. Its ideas come from research, from teaching, from documentation or from the author alone. The [provenance of ideas](../adr/provenance-of-ideas.md#^provenance) requires each idea either to reference a unit of an external source or to be authored. ^exposition

## Referenced and authored ideas

A **referenced idea** presents a unit of an external source, such as a research record, a lesson or a page of documentation. The exposition holds the reference only, and reads the kind and the statement of the unit through the contract of the export of its source. In the architecture of database systems, each group of users reads its own external schema, a view derived from one conceptual schema, and no view stores data of its own [tsichritzis1978]. Literate programming draws a document for human readers and a program for the machine from one source [knuth1984]. A referenced idea stands to its source as such a view stands to its store. Therefore, a correction of a referenced idea goes to its source, and the exposition is then rendered again. ^referenced-idea

An **authored idea** has no source outside the exposition, and declares its function for the reader: an illustration, an analogy, a motivation, or a premise granted by the audience. The exposition is the only source of an authored idea, so a correction of that idea goes to the exposition. ^authored-idea

In an exposition bound to its sources, the subject of the exposition separates the two forms. An idea that could be true or false of that subject references a unit of a source, under the [rule on source-bound expositions](../adr/provenance-of-ideas.md#^source-bound). For an exposition of research, the ground of that rule lies in the theory of inquiry of `gnomon`. Under its [criterion of an epistemic activity](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/docs/epistemology/definitions/activities/epistemic-activities.md#L24), an operation is epistemic only when its output bears on the questions, the knowledge or the warrants of an inquiry. Presenting a result outputs a text, so an exposition leaves the content and the warrant of a research unit unchanged.

A **synthesis** restates or summarizes referenced units, and takes neither form. A synthesis is a [device that adds no idea](../adr/provenance-of-ideas.md#^syntheses): it presents the same referenced ideas again.

## Rhetorical relations

Rhetorical Structure Theory separates two kinds of relation between the spans of a text [mann1988]:

- a **subject-matter relation**, such as a cause, a condition or an elaboration, relates the contents of two spans, and its intended effect is that the reader recognizes the relation between those contents;
- a **presentational relation**, such as a motivation, a background or an evidence, aims to increase an inclination of the reader, such as belief, desire or the ability to understand.

A device realizes each relation in the text, such as a connector, an announcement or a synthesis. ^relation-kinds

An evidence is a presentational relation, since its intended effect is the belief of the reader in a claim. An evidence produces that belief through a relation between the contents of its two spans: one span supports the other. Likewise, an antithesis produces the positive regard of the reader for one span through the incompatibility of two spans. Therefore, an evidence between two referenced ideas requires a recorded support, and an antithesis requires a recorded incompatibility, among the [requirements of a relation on the export](../adr/provenance-of-ideas.md#^relation-requirements). Every other presentational relation, such as a background or a motivation, holds independently of the relations between units recorded by the source. ^evidence-reading

## The audience

The **audience** of an exposition is a readership described by its knowledge, its skills and its register. An audience record states these properties, under the [decision on audiences](../adr/audiences.md), and the record of an exposition names its audiences. ^audience

Argumentation is relative to the audience that it addresses: it seeks the adherence of that audience, and starts from premises that the audience grants [perelman1958]. Therefore, the audience changes five properties of an exposition:

- the **selection** of ideas, since an idea that the audience already holds can be named instead of presented;
- the **order** of ideas, and the moves that deliver them;
- the **authored ideas**, since an illustration, an analogy or a motivation serves the knowledge and the practice of one audience;
- the **names** in which the ideas are stated, which the [glossary of the project](glossary.md#^glossary) admits or forbids for that audience;
- the **granularity** of the presentation, such as the steps of a derivation that are shown.

The audience changes neither the content nor the warrant of a referenced idea. The warrant of a claim of a source is fixed by that source, such as the grounds and the assessment of a research claim, which do not depend on the reader.

> [!WARNING] Departure from the theory of argumentation
> In the new rhetoric, a speaker may introduce a premise because the audience grants it [perelman1958]. In an exposition bound to its sources, a premise granted by the audience stays authored only when it concerns other matters, such as the practice of the audience. A premise about the subject of the exposition is a claim of its sources, so it is first recorded as a unit of a source.

## Distinctions

- **The order of an exposition is free relative to the order of research.** In `gnomon`, the itinerary records the order in which the acts of an inquiry ran. An exposition orders its ideas for its audience, for instance a claim before its support, so its order need not follow the itinerary.
- **A rhetorical move differs from an epistemic act.** A move is a unit of a text that performs one communicative function [swales1990] [swales2004]. An epistemic act produces an epistemic object and is judged by the norm of its activity. A move is judged by whether it delivers its ideas to its audience.

---
## Sources

> [!NOTE] Status of the claims
> - **Established:** external schemas over one conceptual schema, literate programming, the relations of Rhetorical Structure Theory, the relativity of argumentation to its audience, and rhetorical moves, as cited.
> - **Proposals:**
> 	- the analogy between a referenced idea and a view over a store;
> 	- the reading of an evidence and of an antithesis as presentational relations whose effect rests on a recorded relation;
> 	- the five properties of an exposition that its audience changes, and the departure from the new rhetoric.

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [knuth1984] ◐ [Knuth, "Literate programming", *The Computer Journal* 27(2), 97–111, 1984](https://doi.org/10.1093/comjnl/27.2.97)
- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); subject-matter and presentational relations
- [perelman1958] ◐ Perelman & Olbrechts-Tyteca, *La nouvelle rhétorique : traité de l'argumentation*, Presses Universitaires de France, 1958; translated by Wilkinson & Weaver as *The New Rhetoric: A Treatise on Argumentation*, University of Notre Dame Press, 1969; argumentation relative to its audience, §§1–4 and Part Two, checked through [Hitchcock's discussion notes](https://humanities.mcmaster.ca/~hitchckd/perelmandiscussion.htm)
- [swales1990] ○ Swales, *Genre Analysis: English in Academic and Research Settings*, Cambridge University Press, 1990; the rhetorical move
- [swales2004] ◐ [Swales, *Research Genres: Explorations and Applications*, Cambridge University Press, 2004](https://doi.org/10.1017/CBO9781139524827); pp. 228–229, the definition of a move, checked through secondary quotations
- [tsichritzis1978] ◐ [Tsichritzis & Klug (eds.), "The ANSI/X3/SPARC DBMS framework report of the study group on database management systems", *Information Systems* 3(3), 173–191, 1978](https://doi.org/10.1016/0306-4379(78)90001-7); external, conceptual and internal schemas
