---
tags:
  - decision
status: accepted
created: 2026-10-31
revised: 2026-11-01
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Glossaries
---
# Glossaries

> [!QUESTION] Goal: to what does an entry of a glossary refer, how is a glossary bound to an exposition, and what does `ekthesis` check on glossaries?

The [decision on terminology, audience and project specifications](terminology-audience-project-specifications.md) gives the mechanism of glossaries to `ekthesis`. The [decision on glossary entries](concepts-glossaries-notations.md) fixes the content of an entry: the names of one concept, its forbidden forms with their audiences, and the imports that compose a glossary. Three points remain open: the target of the reference from an entry to its concept, the binding of a glossary to an exposition, and the checks. Today, the project and audience schemas of `geonexus` reference its glossary schema by `$ref`.

## Decision

**Reference to a concept.** Each entry of a glossary designates its concept by a reference to the unit that states the concept. That unit may be a concept record of `gnomon`, a definition in a course, or a page of documentation. The entry may hold a gloss written for the audience of the glossary. That gloss restates the meaning stated by the referenced unit and adds no content, as a [synthesis](provenance-of-ideas.md#^syntheses) does, so the referenced unit stays the one source of the meaning. The reference takes the form of a [referenced idea](argument-record.md#^referenced-idea): a relative link until the source publishes an export, then a logical target. ^concept-reference

**Binding.** The record of an exposition names the glossary that binds its text. When the record names none, the glossary named by the binding of its project applies. ^binding

**Checks.** `ekthesis check` runs the rules of the decision on glossary entries on each glossary, and resolves each reference to a concept. On an exposition, the check scans the statements of its ideas and the titles of its parts for the forms that its glossary forbids for its audiences. ^glossary-checks

## Constraints that decide the form

- **A glossary defines no concept.** The meaning of a concept has one source, the unit that states it. A gloss of an entry restates that meaning for an audience, as the [theory of the glossary](../theory/glossary.md#^glossary) states.
- **The ideas of an exposition come from any activity.** A course or a piece of documentation has no concept records of `gnomon` behind its terms. Therefore, a glossary cannot require that every concept be recorded in `gnomon`.
- **A field refers to another field only by a logical target.** Under the decision of `geonexus` on [tool roles](https://github.com/esther-poniatowski/geonexus/blob/827474dca64daef110b9d7fe36a4127c2b32b167/docs/_decisions/tool-roles.md), a record of one field names a record of another field by a logical target typed by its contract.
- **A text has one glossary.** The decision on glossary entries binds one text to one glossary, so a binding needs one rule of precedence between an exposition and its project.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| An entry defines its concept in its own gloss | A glossary reads without its sources | Then, the meaning of a concept has two sources, against the decision on glossary entries |
| An entry references a concept record of `gnomon` only | One kind of target | A glossary of a course or of documentation requires research records for every concept |
| An entry references the unit of any source that states the concept, and may restate it for its audience | One source of meaning, for any exposition and any audience | Each source stating concepts must publish them, as linked units or as an export |
| The project alone binds its glossary | One binding per project | When the audience of an artifact needs another glossary, the artifact cannot change it |

The present decision takes the third option for the reference, and binds a glossary by the exposition first and by its project otherwise.

## Consequences

- The schema `ekthesis:glossary@1` replaces the glossary schema of `geonexus`, in the order of extraction set by the decision on tool roles. Until then, the record of an exposition links its glossary in the format of `geonexus`, and `ekthesis` checks no glossary.
- The contract of an export admits a concept as a presented unit, whose statement is its gloss.
- The decision of `gnomon` on terminology left open whether a glossary entry is the lexical face of a concept record. The present decision answers it: each entry names the concept unit that it references, in any source.
- The scan of forbidden forms adds a rule to `ekthesis check`. That rule reads the audiences of an exposition, with their ancestors and descendants, under the [decision on audiences](audiences.md).
