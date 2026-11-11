---
tags:
  - proposal
index: "[Proposals](docs/proposals/_index.md)"
aliases:
  - Proposals for the specification of an argument
---
# Proposals for the specification of an argument

The goal-oriented specification of arguments, carried from `geonexus`, fixes the argument of a text before its prose is drafted. Then, a checker can test the function of each idea and its connection to the goal of the text. `ekthesis` already decides most of that design:

- the [record](../adr/argument-record.md#^record) states each idea, each relation and each part before the prose;
- the [registries](../adr/argument-record.md#^registries) hold a closed set of relations, and each entry of the record names one relation;
- the [direction](../adr/argument-record.md#^direction) runs each relation from the satellite to the nucleus, so each idea points at the idea that it serves;
- a multinuclear relation joins two nuclei, as the [registry of relations](../../src/ekthesis/data/registries/relations.yml) states for each entry;
- the record states the function of an idea by its relations, whereas the status of a unit belongs to its source, as the [units of an export](../adr/export-contract.md#^export-units) carry it.

The proposals below hold the parts of that design still open, each with the failures that motivate it. The rules of `geonexus` on the status of a target are dropped, since the status of a unit is fixed by its source. In research, `gnomon` splits that status into the route, the support and the attitude of an answer, as its [status and support](https://github.com/esther-poniatowski/gnomon/blob/21a7c33523c4d81754df4d3c8af3c5415b1b592c/docs/specification/answer.md#^status-and-support) state. The routing of an edit through the specification, and the phases of drafting, stay rules of process in `geonexus`.

## Lessons from two revisions

The revision of a thesis project description in `geonexus` went through two outlines and three rounds of review, and the later drafts of a brief failed the review again. Each observed failure fixes one requirement, and `ekthesis` meets some of them already: ^lessons

| Failure observed | Requirement | Where `ekthesis` stands |
| --- | --- | --- |
| The first outline gathered ideas by topical similarity, so its sections chained statements without deriving them. | Each idea declares its relation to another idea before any prose is written. | Met by the relations of the [record](../adr/argument-record.md#^record). |
| The function of each idea stayed implicit, and the status of an item classified its epistemic weight, not its function. | The function of each idea is typed apart from its status. | Met: the relation states the function, and the source states the status. |
| Several links named a topic shared by two items, not an inference. | Each relation is drawn from a closed list, so that a checker can test it. | Met by the [registries](../adr/argument-record.md#^registries). |
| One sentence per item stated both why the item followed and why it came next. | Support and order are specified apart. | Proposed in the [order of ideas](order-of-ideas.md#^order-rules). |
| Sections were added without a statement of their output. | Each part declares the ideas that it establishes. | Proposed as the output of a level in the [assembly schema](assembly-schema.md). |
| Each paragraph reached the goal through some relation, yet did not answer the question left open by its predecessor. | A transition joins each pair of consecutive ideas. | Proposed in the [transitions](order-of-ideas.md#^transitions). |
| A connector carried a valid type and a false content, such as "Therefore, nonlinear networks require three analyses". | An inference names the warrant that licenses it. | Proposed in the [warrants](#^warrants) below. |
| Paragraphs existed because a topic was expected at that place. | Each paragraph declares its goal. | Proposed as the output of a level in the [assembly schema](assembly-schema.md). |
| No check confirmed that the prose realizes the specification. | The prose is reconstructed by a reviewer and compared with the record. | Proposed in the [check by reconstruction](#^reconstruction) below. |
| Under a word budget, the motivating sentences were cut first. | A cut removes whole ideas. | Proposed in the [cuts](#^cuts) below. |
| Declared terms, such as "reference structure", were unknown to the jury. | Each term is checked against the knowledge of the audience. | Owned by Onomasia, through the lexical rules scoped by audience that the amendment of the [decision on audiences](../adr/audiences.md) states. |

**Retired source.** [Lessons from one revision](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L24-L34) in the goal-oriented specification of arguments, and [where it falls short](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L14-L21) in its audit, both in `geonexus`.

## Reachability from the root

Every idea of an exposition must reach its root through a chain of relations, each run from its satellite to its nucleus. Then, a check can report an idea that reaches no root as irrelevant. Rhetorical Structure Theory rests on the same structure, in which each satellite serves a nucleus and the whole text reduces to one central nucleus [mann1988]. The record names no root yet, so the check waits for a field naming it, as the task [`root-reachability`](../../TODO.md) records. ^reachability

Two consequences follow:

- **Forward consequences.** A consequence of the central claim is the nucleus of an `evidence` whose satellite is the central claim. Therefore, the chain runs from the root to the consequence, and the consequence reaches the root only when the record names it as a second root. The registry holds no relation from a consequence to the claim from which it follows. `non-volitional-result` presents the result of a situation: that relation is causal, not logical. *(Inference: the reading of `non-volitional-result` is drawn from its description in the registry.)* The task [`forward-consequence`](../../TODO.md) records the gap.
- **Coordinate ideas.** Some ideas serve one nucleus jointly and in parallel, such as the two obstacles of a problem. Each of them relates to the nucleus by a relation of its own, such as two evidences, and an announcement presents their parallelism, as the [announcements](assembly-schema.md#^announcements) state for coordinate components. *(Inference: the registry holds no multinuclear relation for a joint list, so the parallelism is carried by the announcement rather than by a relation.)*

**Literature.** [mann1988].

**Bears on.** The [record](../adr/argument-record.md#^record), and the [selection from the root](../theory/selection-of-ideas.md#^from-the-root).

**Retired source.** [Goal orientation](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L49-L58) in the goal-oriented specification of arguments of `geonexus`.

## Granularity of an idea

An idea is the smallest unit that holds one relation to its nucleus: one proposition, typically one sentence. A paragraph of the prose groups several ideas, such as a claim and its example, and the drafting chooses that grouping. A finer granularity makes each relation testable, at the cost of a longer record. A referenced idea cannot be finer than the unit that it references, since the export names units and their segments, as the [units of an export](../adr/export-contract.md#^export-units) state. *(Inference: the bound follows from the reference by identifier.)* ^granularity

**Literature.** None cited.

**Bears on.** The ideas of the [record](../adr/argument-record.md#^record).

**Retired source.** [Granularity of an idea](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L122-L124) in the goal-oriented specification of arguments of `geonexus`.

## Warrants referenced, never authored

The audit of `geonexus` proposed that each inferential link carry a one-sentence warrant, in the sense of Toulmin [toulmin1958], so that a false "therefore" surfaces as a warrant that cannot be written. An exposition cannot author that warrant, since the warrant of a claim of a source is fixed by that source, as the [constraints on provenance](../adr/provenance-of-ideas.md#constraints-that-decide-the-rule) state. In `gnomon`, a relation `supports` or `tests` may carry a `warrant`: a mode of inference with a reading, in the relations row of the [elements of an answer](https://github.com/esther-poniatowski/gnomon/blob/21a7c33523c4d81754df4d3c8af3c5415b1b592c/docs/specification/answer.md#^answer-elements). Only `supports` maps onto a class of the export, the class `support` that an `evidence` requires. Therefore, an `evidence` between two referenced ideas can cite the warrant of the support that licenses it, and a relation `tests` carries no warrant to an exposition. ^warrants

The export carries no warrant yet. The contract admits a field only when a check reads it, under the [constraints that decide the contract](../adr/export-contract.md#constraints-that-decide-the-contract). Therefore, the field for the kind and the reading of a warrant must enter the contract together with the check that reads it, as the task [`warrant-field`](../../TODO.md) records. The task `warrant-export` of the task list of `gnomon` exports the warrant once the field exists. Then, a false "therefore" surfaces either as an `evidence` whose support records no warrant, or as an `evidence` without a recorded support. The [severities of the check](../adr/argument-record.md#^severities) already report the second case. The repair of a false "therefore" goes to the source: the missing premise becomes a unit of the source, or the relation of the exposition changes.

**Literature.** [toulmin1958].

**Bears on.** The [required classes](../adr/argument-record.md#^required-classes), and the [relations of an export](../adr/export-contract.md#^export-relations).

**Retired source.** The [third improvement](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L31) of the audit of the goal-oriented specification, and the [warrants](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/exposition-pilot-profile.md#L108) of the exposition pilot profile, both in `geonexus`.

## Check by reconstruction

A check of connectors confirms that the expected words appear in the prose. Such a check detects neither an idea present in the record but absent from the text, nor a connector added to a chain of ideas accumulated by topic. Therefore, a reviewer who has not seen the record must rebuild, from the prose alone, the ideas, their relations and their order. The reconstruction runs from the global level down: first the parts and the output of each part, then the ideas of each part and their relations. The reviewer reads the text as its reader sees it, with folded content left folded. Finally, the rebuilt structure is compared with the record, and each missing idea, each extra idea and each changed relation is a defect. ^reconstruction

**Literature.** None cited.

**Bears on.** The [record](../adr/argument-record.md#^record), the [views](assembly-schema.md#^views), and the [transitions](order-of-ideas.md#^transitions).

**Retired source.** The [fifth improvement](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L33) of the audit of the goal-oriented specification of `geonexus`.

## Cuts bound to ideas

Under a budget of words, a cut leaves out whole ideas, beginning with those whose [retention test](../theory/selection-of-ideas.md#^retention) holds for the fewest readers of the audience. A cut never shortens a transition, a connector or the reference to a warrant, since each of them carries a relation of the record. A budget per part waits for an artifact that declares one. ^cuts

**Literature.** None cited.

**Bears on.** The [retention test](../theory/selection-of-ideas.md#^retention), and the parts of the [record](../adr/argument-record.md#^record).

**Retired source.** The [sixth improvement](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L34) of the audit of the goal-oriented specification of `geonexus`.

## Two tiers of cost

A full specification costs more than a link sentence per item. The cost is justified for a text that a reader evaluates for its argument, such as a proposal or an introduction, and not for a note that records an observation. Two tiers bound the cost: ^tiers

- the **light tier** keeps one chain of ideas per part, each idea with the question that it answers, its transition and its relation toward the root;
- the **full tier** keeps every relation, the strategy of each part, and the check by reconstruction.

Two further limits bound both tiers. First, two authors may type the same relation differently: annotators of discourse relations agree less often on the label of a relation than on the structure of the text [carlson2003]. The registry describes each relation, but states no test that decides between two plausible relations. A test per relation, and a decision rule for each hard pair, would reduce that disagreement without removing it. Candidate hard pairs are `elaboration` against `evidence`, `background` against `elaboration`, and `condition` against `concession`. *(Inference: these pairs are proposed by this note, and no annotation of an exposition has measured them yet.)* Second, a valid record does not make a fluent text. The record fixes the function of each sentence, and the rules of writing govern its wording.

**Literature.** [carlson2003].

**Bears on.** The [registry of relations](../../src/ekthesis/data/registries/relations.yml), whose entries hold a description and no test.

**Retired source.** [Limits](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L138-L144) in the goal-oriented specification of arguments, and the [closing recommendations](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L39-L43) of its audit, both in `geonexus`.

## Checks that a validator can run

A specification in this form admits checks that an outline in prose could not admit. Each check below either exists, belongs to a proposal, or is owned by another tool: ^checks

| Check | State |
| --- | --- |
| Each relation is drawn from the registry, and names existing ideas. | Implemented by `ekthesis check`. |
| Each idea reaches a root. | Proposed in the [reachability](#^reachability) above. |
| No two ideas hold mononuclear relations toward each other in both directions. | Proposed here. |
| The order of each part respects the fixed rules and its strategy. | Proposed in the [strategy of a part](order-of-ideas.md#^strategies). |
| A relation joins each pair of consecutive ideas. | Proposed in the [transitions](order-of-ideas.md#^transitions). |
| A connector of the family of its relation verbalizes each relation. | Waits on the task [`relation-devices`](../../TODO.md). |
| Each term is defined earlier, bound by the glossary, or known to the audience. | Owned by Onomasia. |

The check that the status of a target agrees with its support is dropped, since no rule of an exposition reads the status of a unit.

**Literature.** None cited.

**Bears on.** The command `ekthesis check`, and the [record](../adr/argument-record.md#^record).

**Retired source.** [Checks that a validator can run](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L126-L136) in the goal-oriented specification of arguments of `geonexus`.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [carlson2003] ○ Carlson, Marcu & Okurowski, "Building a discourse-tagged corpus in the framework of Rhetorical Structure Theory", in van Kuppevelt & Smith (eds.), *Current and New Directions in Discourse and Dialogue*, Springer, 85–112, 2003; agreement of annotators on structure and on labels, cited without a check, as the source note already marked it
- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the nucleus and the satellite
- [toulmin1958] ○ Toulmin, *The Uses of Argument*, Cambridge University Press, 1958; the warrant of an argument
