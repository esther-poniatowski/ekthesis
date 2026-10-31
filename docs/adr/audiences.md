---
tags:
  - decision
status: proposed
created: 2026-10-31
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Audiences
---
# Audiences

> [!QUESTION] Goal: what does an audience record hold, how does it refer to concepts and to other audiences, and which records name it?

The [audience](../theory/exposition.md#^audience) of an exposition is a readership described by its knowledge, its skills and its register. The [decision on terminology, audience and project specifications](terminology-audience-project-specifications.md) gives the mechanism of audiences to `ekthesis`. `geonexus` already declares audiences, one file per readership. Its decisions on [audience knowledge by reference](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-knowledge-by-reference.md) and on [audience subtypes](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-subtypes.md) fix the form of those files. In that form, a knowledge item references a term of a glossary.

## Decision

**Content.** An audience record describes one readership, independently of any project:

- its identity, with a label and a gloss;
- its knowledge, as a list of items;
- its evaluation: the conditions under which the readers accept a claim, and the constructions that they cannot assess;
- its register: the forms and tokens that the readers do not share, each with its replacement;
- optionally, its parents and its representatives. ^audience-content

**Knowledge.** A knowledge item references the unit that states a concept, in the same form as an [entry of a glossary](glossaries.md#^concept-reference). The item adds the depth of the content known, from `basic` to `research`, and the skill of the readers with the concept, from `reads` to `develops`. A concept stated by no source yet is named as undeclared, and reported as a warning. A concept that the readers do not hold is absent from the record. ^knowledge

**Subtypes.** An audience may narrow parent audiences, and no chain of parents returns to the audience. A subtype inherits the knowledge and the register of each parent, and its own item on a concept replaces the inherited item on that concept. A text addressed to an audience is bound by the registers of that audience, of its ancestors and of its descendants. ^subtypes

**Names of an audience.** The record of an exposition and the binding of a project name their audiences. A record of another field, such as a contact profile naming the readerships of a researcher, names an audience by a logical target typed by the audience contract. A representative of an audience names the contact profile of a researcher in the same way. ^audience-names

## Constraints that decide the form

- **An audience serves every project.** A readership exists apart from the projects that address it, so an audience record names no form of a project. The forms forbidden by a project for an audience stay in its glossary, under the [decision on glossary entries](concepts-glossaries-notations.md).
- **The meaning of a concept has one source.** If a knowledge item restated a concept, every audience would repeat its classification. If the item referenced a term of a glossary, the audience would depend on the glossary of one project.
- **Shared knowledge is declared once.** The readerships of one field share knowledge and register rules. A parent audience declares them once for its subtypes.
- **A field refers to another field only by a logical target.** Under the draft decision of `geonexus` on [tool roles](https://github.com/esther-poniatowski/geonexus/blob/0712bb5136960141f82ec65d5ae475834293af4a/docs/_decisions/tool-roles.md), Anagraphe checks each logical target and its contract. Therefore, `ekthesis` does not resolve a contact profile itself.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| Knowledge items with typed fields restating each concept | An audience record reads alone | Every audience repeats the classification of each concept |
| Knowledge items referencing the terms of a glossary, as in `geonexus` | The lexicon of a project serves its audiences | Then, an audience depends on the glossary of one project |
| Knowledge items referencing the units that state concepts | An audience serves every project, and each concept keeps one source of meaning | A concept stated by no source stays undeclared until a source states it |
| Flat audiences without parents | One record per readership, with no inheritance | The knowledge and the register shared by the readerships of a field are repeated in each record |

The present decision takes the third option for knowledge, with parents for shared knowledge.

## Consequences

- The schema `ekthesis:audience@1` replaces the audience schema of `geonexus`, in the order of extraction set by the decision on tool roles. Its knowledge items no longer resolve through the imports of a glossary.
- The audience records stay in the content of the consumer, such as the folder `audiences/` of `geonexus`. `ekthesis` provides their schema, their template and their checks.
- The check resolves the parents of an audience, reports a cycle among them, resolves the references of its knowledge items, and reports each undeclared concept as a warning.
- No check reads the knowledge of an audience yet: the knowledge serves the author until a check or a view uses it.
