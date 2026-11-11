---
tags:
  - proposal
index: "[Proposals](docs/proposals/_index.md)"
aliases:
  - Proposals on the order of ideas
---
# Proposals on the order of ideas

The goal [`exposition-order-strategy`](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/TODO.md), carried from `geonexus`, asks that an exposition declare the strategy that orders its parts, and that a check compare the order of the parts with that strategy. The record of an exposition already lists the ideas of each part in reading order, as the [record](../adr/argument-record.md#^record) states, and its relations state support and framing. The order of an exposition is free relative to the order of research, as the [distinctions of an exposition](../theory/exposition.md#distinctions) state. The proposals below derive the order from the relations of the record, and fix the relation that joins two consecutive ideas.

## Support and order apart

A relation states why one idea serves another, and the order of a part states which idea comes first. The revision of a project description in `geonexus` showed the cost of merging the two. Each item carried one sentence that stated both why the item followed from the previous one and why it came next. As a result, the items had to be reordered by hand. Therefore, the order must be read from the parts, and the relations may constrain it by the fixed rules and by the strategy of the part only. ^order-rules

Two relations fix the order of their ends under every strategy of the part:

- a problem or a question, the source of `solutionhood`, precedes its answer;
- a framing idea, the source of `background`, precedes the idea that it frames.

Every other relation leaves the order to the strategy of its part. A reading need that the relations do not state is itself a relation `background`, so the order needs no separate graph of prerequisites. Onomasia checks that a term is defined before its use, through the glossary bound to the exposition, as the amendment of the [decision on glossaries](../adr/glossaries.md) states.

`geonexus` also required a claim to precede its proof. The registry records a proof as an `evidence`, like any other support, so the order of a proof follows the strategy of its part. That loss is accepted. *(Inference: the registry names no relation for a proof alone.)*

**Literature.** None cited.

**Bears on.** The [record](../adr/argument-record.md#^record), whose parts hold the order.

**Retired source.** [Support and order](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L87-L95) in the goal-oriented specification of arguments of `geonexus`.

## Strategy of a part

A part declares one token of each of two pairs. Each pair governs the relations whose two ends the fixed rules leave free: ^strategies

- **Support pair.** A part declared `claim-first` states its nucleus before the satellites of `evidence` and `non-volitional-cause`, as the pyramid principle recommends for a reader who needs the answer first [minto1987]. A part declared `support-first` presents those satellites first and reaches the nucleus last.
- **Generality pair.** A part declared `general-first` states the nucleus of an `elaboration` before its satellites, and a part declared `specific-first` states them after.

*(Inference: in `geonexus`, the support pair governed the relations of grounding only; the relation `non-volitional-cause` joins it here because it orders an effect relative to its cause in the same way.)*

A check compares the order of each part with the fixed rules and with the strategy of the part. The relations of one part can require incompatible orders. Such a conflict arises in a part declared `claim-first` and `general-first`. There, when an idea is the evidence of a claim and also the nucleus of an elaboration by that claim, the idea must both follow and precede the claim. In that case, the check reports each constraint that it drops to break the cycle.

**Literature.** [minto1987].

**Bears on.** The goal [`exposition-order-strategy`](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/TODO.md), and the parts of the [record](../adr/argument-record.md#^record), still without a strategy.

**Retired source.** [Support and order](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L87-L95) and [the checks that a validator can run](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L134), in the goal-oriented specification of arguments of `geonexus`.

## Question before its results

A result stated before the question that it bears on is justified only afterwards, once the question appears. At the moment of reading, the reader has no criterion for judging why that result was selected rather than another. Under the theory of the question under discussion, an assertion is perceived as coherent only when it answers, fully or partially, a question already active in the discourse [roberts2012]. The given–new contract [haviland1974] and the positions of topic and stress [gopen1990] describe the same effect: new information placed before any expectation carries no perceived function. Therefore, the question that makes a result relevant must be active before the result is stated, at every level: ^question-first

- across the exposition, through a superordinate question;
- across the parts, through declared subquestions or lenses;
- within a sentence, through subordination.

The question made active first need not be the research question. An introduction should open on a superordinate question, broad and accepted by the field. Next, the introduction should present the prior results as answers to subquestions of that question. The research question emerges last, as the subquestion that the cited results leave unanswered.

Each of these questions is a question record of a source, presented as a referenced idea. In `gnomon`, a subquestion is linked to its question by `subquestion-of`, among the [links between questions](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/epistemology/objects/question/question.md#^linked-questions). The [registry of relations of `gnomon`](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/src/gnomon/data/registries/relations.yml) exports that link as the class `elaboration`, with the form whole and part. Therefore, the exposition must relate a subquestion to its question by `elaboration` with that form. The relation `solutionhood` runs from each subquestion to the prior result that answers it. The research question is a subquestion with no accepted answer. The [assembly view](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/adr/assembly-of-a-level.md#^assembly-view) of `gnomon` lists such a subquestion among the gaps of its level. Consequently, the fixed rule of `solutionhood` places each question before its results.

Five devices make a question active before the results:

- **Declarative question**: the question is stated as an open state of knowledge rather than as an interrogative;
- **Puzzling property**: the first sentence introduces the object through a property that calls for explanation, and the prior results follow as attempts to account for it;
- **Selection lens**: a framing clause announces the criterion that selects the results before any result is stated;
- **Desideratum**: the first sentence states a property that the field seeks, and the results measure the distance that remains to it;
- **Subordination**: the result takes a subordinate clause, and the open issue takes the main clause, in the stress position.

**Literature.** [roberts2012], [haviland1974], [gopen1990].

**Bears on.** The parts of the [record](../adr/argument-record.md#^record), and the [prior results in a motivation](../theory/selection-of-ideas.md#^prior-results): that note selects the results, and this order places them.

**Retired source.** [Establishing the question under discussion](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/writing/introduce-question.md) in the writing practice of `geonexus`.

## Transitions between consecutive ideas

In the drafts of a brief examined in `geonexus`, each paragraph reached the goal of its text through some relation, yet did not answer the question left open by the paragraph before it. A transition fixes that defect. Every idea of a part except the first relates to its predecessor in reading order by a relation of the record, and that relation serves as its transition. When the relations already recorded join no pair of consecutive ideas, the record adds one between them. A check reports each pair of consecutive ideas that no relation joins. ^transitions

The relation `background` cannot serve as a transition. Almost any earlier idea frames a later one. Therefore, `background` holds between nearly every pair of ideas, and carries no information about their sequence. `background` remains admitted between two ideas when it serves no transition. A chain of ideas accumulated by topic, joined by "moreover", has no relation in the registry, so it cannot pass as a sequence of transitions.

Each idea addresses either the object of its part or a question raised by its predecessor. Such a question is a question record of a source, presented as a referenced idea, and the relation `solutionhood` runs from that question to the idea that answers it. The registry holds no relation by which an idea raises a question for the reader, as the task [`raised-question`](../../TODO.md) records.

A connector verbalizes each transition in the prose, from the family of connectors of its relation. The registry lists no connector yet, as the task [`relation-devices`](../../TODO.md) records.

**Literature.** [roberts2012], for the chain of questions under discussion.

**Bears on.** The relations of the [record](../adr/argument-record.md#^record), and the [check of realization](argument-specification.md#^reconstruction) of the prose.

**Retired source.** [Order and transitions](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/exposition-pilot-profile.md#L112-L123) in the exposition pilot profile of `geonexus`, and the [first two improvements](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/audit.md#L25-L30) of its audit.

## Order of the moves of a genre

A genre fixes the order of its main moves, such as establishing a territory, establishing a niche and occupying it [swales1990]. A part declares its move, and a template of the genre fixes the admitted order of the moves. The exposition pilot of `geonexus` fixed one order for a research brief, in which a part may repeat a move: ^moves

| Move | The part delivers |
| --- | --- |
| niche | a problem, with its obstacle |
| question | a question record |
| framework | a definition or a classification |
| model | a definition of the model |
| mechanism | a claim that explains |
| consequence | a claim derived from earlier ones |

A check of the order of the moves needs the kind of each delivered unit. The closed list of the kinds of a unit is deferred to a later version of the export, among the [questions deferred by the contract](../adr/export-contract.md#^export-deferred). The orders of other genres, such as a poster, an article or a proposal, wait for a pilot of each genre.

**Literature.** [swales1990].

**Bears on.** The parts of the [record](../adr/argument-record.md#^record), still without a move.

**Retired source.** [Operations of a part](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/exposition-pilot-profile.md#L77-L88) in the exposition pilot profile of `geonexus`.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [gopen1990] ○ [Gopen & Swan, "The science of scientific writing", *American Scientist* 78(6), 550–558, 1990](https://www.jstor.org/stable/29774235); the topic and stress positions
- [haviland1974] ○ [Haviland & Clark, "What's new? Acquiring new information as a process in comprehension", *Journal of Verbal Learning and Verbal Behavior* 13(5), 512–521, 1974](https://doi.org/10.1016/S0022-5371(74)80003-4); the given–new contract
- [minto1987] ○ Minto, *The Pyramid Principle: Logic in Writing and Thinking*, Pitman, 1987; the answer before its support
- [roberts2012] ○ [Roberts, "Information structure in discourse: towards an integrated formal theory of pragmatics", *Semantics and Pragmatics* 5(6), 1–69, 2012](https://doi.org/10.3765/sp.5.6); the question under discussion
- [swales1990] ○ Swales, *Genre Analysis: English in Academic and Research Settings*, Cambridge University Press, 1990; the moves of a genre
