---
tags:
  - decision
status: accepted
created: 2026-10-29
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Glossary entries apart from concepts
  - Concepts, glossaries and notations
---
# Glossary entries apart from concepts

> [!QUESTION] Goal: which record holds the meaning of a concept, which record holds its names, and how does a glossary compose its sources?

An adversarial review of the glossary formats of `geonexus` found that their checker reports no issue on three instances, although the defects below sit in those instances:

- **checks declared and never run**: inverse pairs, the acyclicity of narrower terms, and the language of expressions;
- **one entry holding two kinds of fact**: a glossary term mixes the meaning of a concept with its names, so two glossaries define one concept differently, and forbid one form with different replacements;
- **exceptions copied entry by entry**, two of which can never apply.

## Decision

**A concept record holds the meaning of a concept.** The concept record belongs to research, and `gnomon` defines it. A concept of another project is referenced, never copied.

**A glossary holds the names of concepts.** Each entry names one concept, with:

- its label and literal variants;
- its patterns of variants;
- its alternative forms with their contexts;
- its names in other frameworks, each with the way to introduce it;
- optionally, a gloss for the audience of the glossary, restating the meaning held by the concept record without adding content.

A forbidden form keeps its replacement, its reason and its severity. The form also states the audiences for which it is forbidden, and an absent list of audiences means every audience, so that audience specifications stay independent of projects. An exception to a forbidden form names a shared exception, such as a mention, a quotation or a citation, or states its own pattern. In both cases, it carries an example that the checker tests.

**A glossary composes its sources by merging imports only.** A text is bound to one glossary, an imported entry resolves its references in its source file, and an entry that shadows an imported one is reported.

## Constraints that decide the formats

- **An unreported rule goes unapplied.** The agents writing these records learn the rules from the reports of the checker, so every declared rule is run, and every rule has a planted case.
- **A concept has one meaning, and several names.** The names of a concept vary with the audience and the context, whereas its meaning does not.
- **A form has one schema construct.** Ekphrasis renders a choice between object schemas, but not a choice decided by required keys only, and it writes defaults into new records. Therefore, each alternative is an object schema, and a status is required rather than defaulted.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| Keep one glossary entry for meaning and names | One file per project | Two projects then define one concept twice, and a name differing by audience duplicates the meaning |
| Move every audience-specific ban to the audience specifications | Glossaries hold only universal bans | An audience specification then names the forms of each project, so it no longer serves every project |

## Consequences

- Each entry of the glossary refers to its concept.
- The forbidden forms carry their audiences, and the register rules of a project stay in its glossary.
- The checker of glossaries rejects any declared check that it does not run, and scans the prose fields of a glossary for forbidden forms.
- The instances of `geonexus` migrate, and their copied exceptions become shared exceptions.
