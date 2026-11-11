---
tags:
  - decision
status: accepted
created: 2026-10-31
revised: 2026-11-11
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Audiences
---
# Audiences

> [!QUESTION] Goal: what does an audience record hold, how does it refer to concepts and to other audiences, and which records name it?

The [audience](../theory/exposition.md#^audience) of an exposition is a readership described by its knowledge, its skills and the claims that it accepts. The [decision on terminology, audience and project specifications](terminology-audience-project-specifications.md) gives the mechanism of audiences to `ekthesis`. `geonexus` already declares audiences, one file per readership. Its decisions on [audience knowledge by reference](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-knowledge-by-reference.md) and on [audience subtypes](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-subtypes.md) fix the form of those files. In that form, a knowledge item references a term of a glossary, and the file declares a register.

The decision of `geonexus` on [designation and typography](https://github.com/esther-poniatowski/geonexus/blob/584a14f134e7b6231eeae31518622439acf10d00/docs/_decisions/designation-and-typography.md) moves the register into the lexical rules of Onomasia, the designation tool, each rule scoped by audiences. It keeps the audience in `ekthesis` as a profile of its readers, and gives `ekthesis` the generation of the *scope table*, which states the ancestors and the descendants of each audience. This revision of 2026-11-11 states the record without its register, the form of a reference to a concept, and the generation of that table.

## Decision

**Content.** An audience record describes one readership, independently of any project. It follows the contract `ekthesis:audience@1`, and holds:

- its identity, under `identity`: an id, a label and a gloss, and optionally its parents under `narrows`, its representatives, and the communities with which it is confused;
- its knowledge, under `knowledge`, as a list of items;
- its evaluation, under `evaluation`: the conditions under which the readers accept a claim (`accepts`), and the constructions that they cannot assess (`cannot_assess`). ^audience-content

The record declares no register. A form that some readers do not share is a lexical rule of a glossary of Onomasia, whose field `audiences` names the audiences that the rule binds.

**Knowledge.** A knowledge item references the unit that states a concept, under `concept`, by its logical target, in the form that Onomasia uses for the field `denotes` of a notation entry. The item adds the depth of the content known, from `basic` to `research`, and the skill of the readers with the concept, from `reads` to `develops`, with optional example skills. A concept stated by no source yet is named under `undeclared`, and reported as a warning. A concept that the readers do not hold is absent from the record. ^knowledge

**Subtypes.** An audience may narrow parent audiences, and no chain of parents returns to the audience. A subtype inherits the knowledge of each parent, and its own item on a concept replaces the inherited item on that concept. A text addressed to an audience is bound by the lexical rules scoped to that audience, to its ancestors and to its descendants. ^subtypes

**Scope table.** `ekthesis` derives the scope table from the parents declared by a set of audience records, in the contract `onomasia:scope-table@1`. The ancestors of an audience are the transitive closure of its parents, and its descendants are the transitive closure of the inverse relation. The command `ekthesis scope-table` takes the audience records and the path of the table, and writes the table. With the option `--check`, the command writes nothing, and reports a table that differs from the one derived from the records. The consumer runs that check in its gate, so a change of parents cannot leave the table stale. ^scope-table

**Names of an audience.** The record of an exposition and the binding of a text name their audiences by id. A record of another field, such as a contact profile naming the readerships of a researcher, names an audience by a logical target typed by the audience contract. A representative of an audience names the contact profile of a researcher in the same way. ^audience-names

## Constraints that decide the form

- **An audience serves every project.** A readership exists apart from the projects that address it, so an audience record names no form of a project. The forms forbidden by a project for an audience stay in its glossary, under the [decision on glossary entries](concepts-glossaries-notations.md).
- **The meaning of a concept has one source.** If a knowledge item restated a concept, every audience would repeat its classification. If the item referenced a term of a glossary, the audience would depend on the glossary of one project.
- **Shared knowledge is declared once.** The readerships of one field share knowledge. A parent audience declares it once for its subtypes.
- **One tool matches the forms of a text.** Onomasia matches the written forms of a text against the rules of its glossaries. A register in the audience record would make Onomasia read a second format, or make `ekthesis` match forms itself.
- **A field refers to another field only by a logical target.** Under the decision of `geonexus` on [tool roles](https://github.com/esther-poniatowski/geonexus/blob/827474dca64daef110b9d7fe36a4127c2b32b167/docs/_decisions/tool-roles.md), Anagraphe checks each logical target and its contract. Therefore, `ekthesis` does not resolve a contact profile itself.
- **Ekthesis reads no configuration file.** The records and the paths of a run are its arguments, as for the command `ekthesis check`.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| Knowledge items with typed fields restating each concept | An audience record reads alone | Every audience repeats the classification of each concept |
| Knowledge items referencing the terms of a glossary, as in `geonexus` | The lexicon of a project serves its audiences | Then, an audience depends on the glossary of one project |
| Knowledge items referencing the units that state concepts | An audience serves every project, and each concept keeps one source of meaning | A concept stated by no source stays undeclared until a source states it |
| Flat audiences without parents | One record per readership, with no inheritance | The knowledge shared by the readerships of a field is repeated in each record |
| A register declared in the audience record | The readers and their forbidden forms read in one file | Onomasia would read the audience format to match forms, which couples the two tools |
| Onomasia deriving the ancestors from the audience records | No generated table | Onomasia would read the audience format; the table keeps the relation between audiences in `ekthesis`, which owns it |
| `ekthesis` resolving the contact profile of a representative | The membership of a representative is checked with the audience | `ekthesis` would read the contact format of the consumer, which a logical target avoids |

The present decision takes the third option for knowledge, with parents for shared knowledge, and leaves both the register and the derivation of ancestors out of the record and out of Onomasia.

## Consequences

- The schema `ekthesis:audience@1` replaces the audience schema of `geonexus`, in the order of extraction set by the decision on tool roles. Its knowledge items no longer resolve through the imports of a glossary.
- The audience records stay in the content of the consumer, such as the folder `audiences/` of `geonexus`. `ekthesis` provides their schema, their template and their checks.
- The check validates each audience record against its schema, resolves its parents and the communities of its confusions among the audience records of the run, reports a repeated id and a cycle among parents, checks the form of each logical target, and reports each undeclared concept as a warning.
- The membership of a representative in the audience, which reads the communities of a contact profile, is checked by the consumer that holds the contact profiles.
- The consumer points the key `texts.scope_table` of its configuration of Onomasia to the generated table, and runs `ekthesis scope-table --check` in its gate.
- No check reads the knowledge of an audience yet: the knowledge serves the author until a check or a view uses it.
