---
tags:
  - decision
status: proposed
created: 2026-10-31
revised: 2026-10-31
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Renaming of a symbol for a venue
---
# Renaming of a symbol for a venue

> [!QUESTION] Goal: may an artifact print a symbol of its source in a form other than the one declared by the notation of that source, and what must `ekthesis` check when it does?

The notation of a research project stays in `gnomon`: its rules of composition, its conventions of typography, and the LaTeX macros generated from its symbols. A researcher writes derivations in that notation. An artifact presents few of those symbols, and its venue may follow other conventions, such as the letters used by a community for a quantity or the typography of its vectors. The contract of the export of a source holds one entry per symbol, with the identifier of the symbol and its LaTeX macro.

## Decision

An artifact may rename a symbol of its source to follow the convention of its venue. A renaming replaces the printed form of one symbol, the expansion of its LaTeX macro, within one artifact. The renaming keeps the identifier of the symbol, so every formula of the artifact still names the symbol by its identifier, and every check of the source still resolves it. ^renaming

The record of the artifact declares its renamings, each as a pair of a symbol identifier and a printed form. A venue holds no renaming of its own. ^renaming-record

From the symbol entries of the contract alone, `ekthesis` checks that no two symbols of one artifact print alike. The symbols of an artifact are the symbols named by its ideas. Two symbols print alike when their printed forms, after the renamings of the artifact, are equal once whitespace is removed. Each renamed identifier must also name a symbol entry of the contract. ^collision-check

## Constraints that decide the rule

- **The notation serves research.** A researcher formulates concepts in the notation and writes derivations with its conventions, so the density and the printed forms required by research do not bind an artifact.
- **The identifier is the key that both tools resolve.** The checks of the source and the references of an exposition resolve a symbol by its identifier. A renamed identifier would break every reference to the symbol.
- **`ekthesis` reads only the contract of an export.** The [provenance of ideas](provenance-of-ideas.md) restricts every check of `ekthesis` to the entries of the contract, so the collision check reads the symbol entries only.
- **A reader tells symbols apart by their printed forms.** Two symbols printed alike in one artifact are read as one symbol, even when their identifiers differ.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| An artifact prints every symbol as the notation declares | One printed form per symbol across all artifacts | The artifact cannot follow the convention of its venue |
| The artifact declares its symbols in a notation of its own | Full control over the printed forms | Each symbol is declared twice, and the formulas of the artifact lose the identifiers that the checks of the source resolve |
| The venue declares the renamings shared by its artifacts | One declaration per venue | A convention of a venue names quantities in general, not the symbols of one project, so each project still maps its symbols onto that convention |
| The artifact maps identifiers onto printed forms, checked for collisions from the contract | The artifact follows its venue, and keeps the identifiers | The collision check needs the symbol entries of an export, and no source publishes an export yet |

The present decision takes the last option.

## Consequences

- The schema of an exposition gains a list of renamings, each holding a symbol identifier and a printed form.
- A rule of `ekthesis check` reports two symbols of one artifact that print alike, and a renaming whose identifier names no symbol entry. Until a source publishes an export, the rule compares the renamed forms with one another only.
- When `ekthesis` renders the LaTeX macros of an artifact, it replaces the expansion of each renamed macro, so the source generates its macros unchanged.
- Equality after the removal of whitespace misses two forms written differently that print alike, such as two commands of the same glyph. The author and the reviewer judge such cases.
