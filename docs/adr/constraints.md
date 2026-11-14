---
tags:
  - decision
status: accepted
created: 2026-11-14
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Venue constraints
---
# Venue constraints

> [!QUESTION] Goal: what does a constraints record hold, how does the record of an exposition name it, and which tool checks each of its properties?

The constraints of a venue are the binding rules that the venue imposes on one kind of exposition, such as a submitted abstract or a printed poster. The [naming patterns of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/c878fe132de3f248703b16efed8a40e445ac980b/docs/rules/naming-patterns.md#venue-documents) define them as the rules extracted from the scope and the instructions of the venue, each with its source. `geonexus` writes them as Markdown notes, one table of constraints per note, beside the event or the artifact that they bind. The decision of `geonexus` on [tool roles](https://github.com/esther-poniatowski/geonexus/blob/6dfa05da353aacdf8c318a687a436a3c8204785b/docs/_decisions/tool-roles.md) assigns the constraints to `ekthesis`, at step 3 of its order of extraction. On 2026-11-14, the researcher decided that the constraints move to `ekthesis` now.

## Decision

**Content.** A constraints record states the constraints of one venue on one kind of exposition. It follows the contract `ekthesis:constraints@1`, and holds:

- its identity, under `identity`: an id, by which the record of an exposition names it, and a title;
- its groups, under `groups`, each with an id, a label and an optional description, when the constraints fall into kinds;
- its sources, under `sources`, each with an id, a label and an optional location;
- its constraints, under `constraints`, in reading order;
- optional notes, under `notes`, in Markdown. ^constraints-content

A constraint holds an id, a label, the requirement as the venue states it, and the ids of the sources that state the requirement. It may name its group, and add a source note: the section of a source that states the requirement, or the part of the requirement that each source states. The notes hold the provenance of the record and the content that binds no exposition, such as the suggestions of a venue or the identification of its event. The record may also carry a block `metadata` reserved to its consumer, as an audience record does; `ekthesis` admits any content there and checks none. ^constraint

**Sources declared once.** A source is declared once, and each constraint cites it by id. A source is a document of the venue, such as its call for abstracts, or a person who relayed a rule. Its location is the address of a page, or the logical target of the record that transcribes the source, such as a note of instructions. A source read nowhere, such as a rule relayed by the author, has no location. ^sources

**Units.** Under [ADR 0006 of Anagraphe](https://github.com/esther-poniatowski/anagraphe/blob/main/docs/adr/0006-logical-targets.md), each group, each source and each constraint is a unit of the record, since its definition declares its identifier by `x-identifier`. The specification of an exposition therefore names the constraint that a decision meets by a logical target, such as `{id: constraints_submission_2026-11_pints, unit: poster-size}`, and names a group of constraints the same way. The units of one record share one namespace, so a group, a source and a constraint take distinct ids. ^units

**Names of a constraints record.** The field `venue-constraints` of the record of an exposition names a constraints record by a logical target typed by the contract `ekthesis:constraints`, without a version, and naming no unit. It still accepts the link to a note of constraints that it held before. Under the [versioning rule of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/6dfa05da353aacdf8c318a687a436a3c8204785b/docs/_decisions/tool-roles.md#shared-conventions), this change makes no valid record invalid and keeps the meaning of the field, so the contract stays `ekthesis:exposition@3`. The entry of `x-target-contract` names no version, because no rule of `ekthesis` reads the fields of a constraints record: ADR 0006 of Anagraphe pins a version only for a field whose tool reads the target record. ^constraints-names

**Check.** `ekthesis check` validates a constraints record against its schema. A conforming record is then checked by the rules that read its identifiers and its references through the annotations of its schema, as for an argument record:

- `unique-identifiers` reports a group, a source or a constraint whose id repeats an earlier item of its collection;
- `existing-references` reports a constraint naming a group or a source that the record does not declare.

Anagraphe checks the rest under its ADR 0006. It resolves the target of `venue-constraints`, and reports a record of another contract as `target-contract-mismatch`. It also reports two records of a repository holding one id, a target naming an absent unit, and a target naming a unit that two items of the record declare. ^constraints-check

## Constraints that decide the form

- **A venue states its rules once.** Every exposition for the venue must meet the same constraints, so the record names no project and no exposition.
- **A constraint carries its source.** A requirement whose source is unknown cannot be verified against the venue, and the sources of a venue age at different rates.
- **A specification answers each constraint.** The specification of an exposition records the decision that meets each constraint, so each constraint needs a stable name that survives the rewording of its label.
- **A field refers to another field only by a logical target.** Under rule 1 of the references across fields of the decision on tool roles, Anagraphe checks each logical target and its contract, and `ekthesis` resolves no target itself.
- **A valid record stays valid within a version.** The record of an exposition that names its constraints by a link must not fail its contract when the constraints become records.

## Options weighed

| Option | Benefit | Reason it is not taken |
| ------ | ------- | ---------------------- |
| Keep the constraints as Markdown notes of `geonexus` | No migration; each note keeps its free layout | No tool checks a note, an exposition names a note by a link that no contract types, and the decision on tool roles assigns the constraints to `ekthesis` |
| Defer the contract until a check of `ekthesis` reads the constraints | The fields are fixed by their first reader | The notes would keep growing in the vault meanwhile, and a specification could name no constraint by a target; a check that reads the record later adds rules without changing its form |
| A source written as text in each constraint, as in the unused schema of `geonexus` | One row reads alone, and the notes convert line by line | The same link repeats on every row of a note, and an abbreviation such as `call` holds its meaning only in the prose of the notes |
| Groups nesting their constraints | The reading order of the groups is the order of the file | A record without groups would need a second form, and moving a constraint between groups would move its text |
| A new version `ekthesis:exposition@4` whose `venue-constraints` admits a target only | One form of the field | Every record that names its constraints by a link would become invalid, before the notes become records |
| `x-target-contract` pinned to `ekthesis:constraints@1` | A new version of the constraints contract is reviewed before an exposition accepts it | Each new version of the constraints contract would force a new version of the exposition contract, although no rule of `ekthesis` reads the target |

The present decision moves the constraints now, declares the sources once, names each group by a reference, and widens `venue-constraints` within `ekthesis:exposition@3`.

## Consequences

- The schema `ekthesis:constraints@1` replaces the Markdown notes of constraints in `geonexus`, with its skeleton `data/skeletons/constraints.yml`, and the unused constraints schema of `geonexus` is retired. The records stay in the content of the consumer, beside the event or the artifact that they bind.
- A source that is neither a page nor a record, such as a PDF without a transcription or a file of a project, has no location in the record. The consumer transcribes it into a record, or names it in the label of the source.
- A consumer that pins the schema `ekthesis:exposition@3` updates it in the same change as `ekthesis`, since a parent registry requires identical bytes for one shared contract.
- The link form of `venue-constraints` is retired by a new version of the exposition contract, once no record names its constraints by a link.
- No rule compares an exposition with its constraints yet: the record serves the author and the specification until such a check reads it.
