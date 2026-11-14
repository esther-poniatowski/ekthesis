---
tags:
  - tasks
aliases:
  - Project goals
---
# Project goals

This list holds the goals of `ekthesis` that span several parts of the project, grouped in families.

## 1. Referenced ideas

A [referenced idea](docs/adr/argument-record.md#^referenced-idea) names a unit of a source and states the kind of that unit, and the check reads no source.

- [ ] Name the owner of the status of a presented unit, such as an entertained or a superseded claim, and of the trace of its conditions. The retired [contract of a research export](docs/adr/export-contract.md#^export-deferred) left them to the exposition pilot of `geonexus`, which is retired too. The next action is to decide whether the record of an exposition states the status of a referenced idea, as it states its [kind](docs/adr/argument-record.md#^referenced-kind). 🆔 presented-unit-status
- [ ] Replace the relative link under `source` of a referenced idea by a logical target of Anagraphe, under `ekthesis:exposition@3`, as [ADR 0006 of Anagraphe](https://github.com/esther-poniatowski/anagraphe/blob/main/docs/adr/0006-logical-targets.md) orders. The [referenced idea](docs/adr/argument-record.md#^referenced-idea) states the interim form; the audience record took the targets in `ekthesis:audience@2`. The one record of an exposition, the argument of the PINTS 2026 poster of Mixture-Input Encoding, stays at `@1` until the project is reconstructed, so no record waits on this version yet. 🆔 logical-target-references
- [x] Retire the contract `ekthesis:audience@1` once no record uses it: remove `audience.v1.schema.yaml`, its entry in `AUDIENCE_CONTRACTS` and in `specs/schema-resources.yml`, and the test of its text targets 🆔 retire-audience-v1 ✅ 2026-11-14
- [ ] Retire the contract `ekthesis:exposition@1` once no record uses it: remove `exposition.v1.schema.yaml`, its entry in `EXPOSITION_CONTRACTS` and in `specs/schema-resources.yml`, and its retained fixture. Its last record is the argument of the PINTS 2026 poster of Mixture-Input Encoding, which stays at `@1` until the project is reconstructed from scratch, as the researcher decided on 2026-11-12. 🆔 retire-exposition-v1

## 2. Relations of the registry

The [registry of relations](src/ekthesis/data/registries/relations.yml) holds the relations of Rhetorical Structure Theory, and the move of the argument conventions of `geonexus` found relations that it does not cover.

- [ ] Decide how an exposition relates a consequence to the claim from which it follows. Under the [direction of a relation](docs/adr/argument-record.md#^direction), a consequence is the nucleus of an `evidence` whose satellite is the central claim, so the consequence reaches no root, as the [reachability from the root](docs/proposals/argument-specification.md#^reachability) states. The relation `non-volitional-result` is causal, not logical. The next action is to weigh a second root against a relation outside Rhetorical Structure Theory. 🆔 forward-consequence
- [ ] Decide how an idea raises a question for the reader. The question is a question record of a source, presented as a referenced idea, and `solutionhood` runs from it to its answer. No relation of the registry joins the idea that raises the question to that question, as the [transitions](docs/proposals/order-of-ideas.md#^transitions) state. The next action is to decide whether a presentational relation of the registry, such as `background`, carries that function, or whether a new relation is needed. 🆔 raised-question
- [ ] Decide how a figure presents an idea of an exposition: as a device that realizes a relation, or as a part of the record. The [kinds of relation](docs/theory/exposition.md#^relation-kinds) name a connector, an announcement and a synthesis as devices, and no figure. The next action is to state the figure among the devices in the theory of an exposition. 🆔 figure-device
- [ ] Add to each entry of the registry of relations a field `devices` that lists the connectors verbalizing the relation, so that a check compares the prose with the record. The [survey of discourse and argument structure](docs/references/discourse-argument-structure.md) states the accounts from which the families of connectors can be drawn. The next action is to draw the connectors of each relation from those accounts and to choose the check that reads them, as the [transitions](docs/proposals/order-of-ideas.md#^transitions) require. 🆔 relation-devices

## 3. Record of an exposition and its check

The [record of an exposition](docs/adr/argument-record.md#^record) states its ideas, its relations and its parts, and its check reads them through the annotations of the schema.

- [ ] Let the record of an exposition state an idea excluded because a reader of a declared audience would expect it. The entry names that audience and the reason, as the [exclusions tied to an audience](docs/theory/selection-of-ideas.md#^exclusions) require. The next action is to weigh a field of the record against an extension of the audience record. 🆔 audience-exclusions
- [ ] Add a field naming the root of an exposition, its central claim or its question. Add a check that reports each idea reaching no root through its relations, as the [reachability from the root](docs/proposals/argument-specification.md#^reachability) proposes. The next action is to decide whether an exposition admits several roots. The task `forward-consequence` bears on that decision. 🆔 root-reachability
- [x] Decide whether the status by which an idea is core or only deepens another one keeps the name `elaboration`, shared with a relation, or takes a name of its own. The researcher kept `elaboration`, as [the name of the status](docs/proposals/assembly-schema.md#^status-name) records 🆔 status-name ✅ 2026-11-11
- [ ] Divide the record of an exposition into an argument, valid for any audience, and a projection for one audience and one venue, as the [decision of `geonexus` on designation and typography](https://github.com/esther-poniatowski/geonexus/blob/20143c8a/docs/_decisions/designation-and-typography.md) states and the notice of the [decision on the argument record](docs/adr/argument-record.md) records. The registry of authored kinds declares the layers that admit each kind. The first record is the poster of Mixture-Input Encoding for PINTS 2026, whose argument the poster for Royaumont reuses. The next action is a proposed revision of the decision on the argument record, for the review of the researcher. 🆔 argument-projection
- [ ] Report a mapping of an audience record that repeats a key, whose earlier value the YAML parser drops. The record checker of `geonexus` reported it until the audience files followed `ekthesis:audience@1`, and no check reports it since. No contract of `ekthesis` reports a repeated key yet, so the next action is to read every record with a loader that records repeated keys, and to report each one under a rule of its own. 🆔 audience-duplicate-keys

## 4. Package data

The package ships data that its consumers read, such as its schemas, its registries and its skeletons.

- [ ] Add a command that writes a skeleton of `src/ekthesis/data/skeletons/`, such as the claim boundaries of an artifact, into a consumer, and fills the metadata that the consumer requires. The skeletons carry the frontmatter keys of `geonexus`, their first consumer, until that command supplies them. The next action is to decide whether the command, or the consumer, owns the frontmatter of a scaffolded note. 🆔 skeleton-scaffold
