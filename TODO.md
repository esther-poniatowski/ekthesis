---
tags:
  - tasks
aliases:
  - Project goals
---
# Project goals

This list holds the goals of `ekthesis` that span several parts of the project, grouped in families.

## 1. Contract of a research export

The [contract of a research export](docs/adr/export-contract.md) carries the units and the relations of a source that the checks of `ekthesis` read.

- [ ] Add to the relation entry of the contract `ekthesis:export@1` a field for the warrant of a relation of class `support`: its mode of inference, such as deductive or abductive, and its reading, which states why the source supports the target. An exposition then references the warrant of a research relation and never authors one. The contract admits only a field that a check reads, as its [constraints](docs/adr/export-contract.md#constraints-that-decide-the-contract) state. The next action is therefore to choose the check that reads the field, such as the check of [required classes](docs/adr/argument-record.md), which already requires a support for each evidence. The task `warrant-export` of `gnomon` waits on this field. 🆔 warrant-field
- [ ] Name the owner of the status of a presented unit and of the trace of its conditions. The [deferred parts of the contract](docs/adr/export-contract.md#^export-deferred) leave them to the exposition pilot of `geonexus`, which is retired. The next action is to state the owner in that decision. 🆔 presented-unit-status
- [ ] Decide whether the relation `tests` of a source reaches an exposition. It carries a warrant in `gnomon` but has no class in the contract, so a warrant of a test cannot be cited. The next action is to decide whether the contract gives it a class. 🆔 test-warrant

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

## 4. Package data

The package ships data that its consumers read, such as its schemas, its registries and its skeletons.

- [ ] Add a command that writes a skeleton of `src/ekthesis/data/skeletons/`, such as the claim boundaries of an artifact, into a consumer, and fills the metadata that the consumer requires. The skeletons carry the frontmatter keys of `geonexus`, their first consumer, until that command supplies them. The next action is to decide whether the command, or the consumer, owns the frontmatter of a scaffolded note. 🆔 skeleton-scaffold
