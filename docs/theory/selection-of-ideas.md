---
tags:
  - theory
index: "[Theory](docs/theory/_index.md)"
aliases:
  - Selection of ideas
---
# Selection of ideas

> [!QUESTION] Goal: which units of its sources does an exposition present to its audience, and by which test does it keep each of them?

The selection of ideas is the first property of an exposition that its [audience](exposition.md#^audience) changes. Selection leaves the source unchanged: when the exposition leaves a unit out, that unit remains a unit of its source, with its grounds and its warrant. Therefore, every test of this note is a test of presentation. Each test asks whether presenting an idea produces an effect on the declared audience, never whether the claim of the source needs that idea in order to hold. In research, the grounds that a claim needs are stated by its source, such as the [grounds and the relations of an answer](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/specification/answer.md#^answer-elements) of `gnomon`. ^presentation-test

## Selection from the root

The root of an exposition is its central idea: the claim that answers the question of the exposition, or that question when the exposition answers none. The ideas are selected from the root outward, one relation at a time. A candidate is a satellite whose nucleus is already selected, under the [direction of a relation](../adr/argument-record.md#^direction), in which the source is the satellite and the target is the nucleus. Therefore, a unit of a source can be a candidate only when it relates to a selected idea. The closeness of its topic to the root admits no unit. Consequently, the size of the selection depends on the argument, and not on the number of units that the source holds. ^from-the-root

Two candidates fall outside that rule. A consequence of the root is the nucleus of an `evidence` whose satellite is the root, so it enters without being a satellite, as the task [`forward-consequence`](../../TODO.md) records. In a multinuclear relation, such as a `contrast`, the second nucleus enters once the first is selected. *(Inference: the source of this rule did not separate satellites from nuclei.)*

## Retention test per relation

Rhetorical Structure Theory defines each relation by the effect that it aims to produce on the reader [mann1988]. Therefore, one test can serve every relation. A satellite passes the test when its nucleus needs the effect of the relation for the declared audience, and no other presented satellite of that nucleus already produces that effect. The condition under which a nucleus needs that effect depends on its relation in the [registry](../../src/ekthesis/data/registries/relations.yml): ^retention

| Relation, from source to target | The satellite is presented when |
| --- | --- |
| `evidence`, from a premise of the derivation of a claim to that claim | the derivation of the claim is presented, and the audience does not grant the premise; a premise that the audience grants may be named instead of presented |
| `evidence`, from a datum or from another support of a claim to that claim | the evaluation of the audience accepts support of that kind, and no other presented evidence of the claim gives support of the same kind |
| `non-volitional-cause`, from a cause to its effect | the question of the exposition, or the evaluation of the audience, asks why the effect holds, and no other presented cause of the effect states it *(inference)* |
| `condition`, from a condition to the idea that holds under it | without the condition, the nucleus as presented would claim more than the domain that its source records |
| `concession`, from a conceded situation to the idea that it seems to oppose | a reader of the audience would hold the conceded situation against the nucleus *(inference)* |
| `antithesis`, from a rival idea to the idea favoured | a reader of the audience would hold the rival idea |
| `contrast`, between two nuclei | a reader of the audience would confuse the two ideas, or the question of the exposition asks how they differ *(inference)* |
| `background`, from a framing idea to the idea that it frames | the audience record lists no knowledge of the concept that the satellite states, or a slot of the venue requires the framing |
| `solutionhood`, from a problem or a question to its answer | the nucleus answers the question of the exposition, or the audience does not already hold the problem that the nucleus solves *(inference)* |
| `elaboration`, from a detail to the idea that it details, with its form | the audience cannot interpret the nucleus at the level of abstraction of its statement, and no other presented elaboration of the nucleus takes the same form *(inference)* |
| any other relation of the registry | the general test above, read through the effect that the registry states for that relation |

A restatement and a summary take no test, since a synthesis is a [device that adds no idea](../adr/provenance-of-ideas.md#^syntheses).

The record of an exposition states the relation, not the use of the satellite in its source, so the two rows of `evidence` cannot be told apart from the record. That use belongs to the record of the source, which `ekthesis` does not read. Therefore, the author and the reviewer must judge which row applies. A premise granted by the audience may concern the subject of a source-bound exposition. That premise still references a unit of a source, as the [rule on source-bound expositions](../adr/provenance-of-ideas.md#^source-bound) requires. An authored premise remains admitted for other matters, such as the practice of the audience.

The test admits an idea. Then, the slots of a venue decide which admitted ideas appear. The slots belong to the venue constraints of the consumer, such as the summary of a conference abstract.

## Exclusions tied to an audience

An exposition records an idea as excluded only when a reader of a declared audience would expect that idea. A specialist may expect an extension of the result, and a reviewer may expect a stronger wording, for instance. The exclusion names that audience, or one of its representatives under the [names of an audience](../adr/audiences.md#^audience-names), and the reason for leaving the idea out. When no audience expects an idea, the exposition leaves the idea out without a record. The exclusion serves the reviewer of the exposition: with that record, the reviewer can tell an idea weighed and left out from an idea overlooked. The record of an exposition holds no field for an exclusion yet, as the task [`audience-exclusions`](../../TODO.md) records. ^exclusions

## Prior results in a motivation

A motivation presents the question of an exposition together with the prior results that lead to it. When these results relate to the question by topical proximity only, a reader cannot tell why they were chosen over others. Therefore, a prior result may be presented in the motivation of a question only when its source records one of three facts that relate it to the problem addressed by the question: ^prior-results

| Role of the prior result | Fact recorded by a research source | Relation presented |
| --- | --- | --- |
| **Delimitation**: the result defines the object or the framework of the question | a concept record, or a law of the background, on which the question rests | `background`, toward the question |
| **Tension**: the result conflicts with another result, an observation or a desideratum | a relation `incompatible-with` between two answers, or the knowledge obstacle `conflict` of the problem | `background`, toward the problem *(inference)* |
| **Non-triviality**: the result shows that a natural approach fails or falls short | a relation `defeats` toward the answer of that approach, or the knowledge obstacle `unwarranted-claim` of the problem *(inference)* | `background`, toward the problem *(inference)* |

The facts are stated in the terms of `gnomon`, through the [relations of an answer](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/epistemology/objects/answer/answer-form.md#^answer-relations) and the [obstacles of a problem](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/specification/problem.md#^stated-obstacles). The three roles all reach the reader through `background`, since each role increases the ability of the reader to comprehend the problem. Therefore, the record of the exposition loses the distinction between the roles, whereas the source keeps it. The problem itself is presented as the satellite of `solutionhood` toward the answer.

A deletion test applies to each prior result that holds one of these roles. When the removal of a prior result leaves the question as determinate, as justified and as urgent, the result is ornamental. Such a result moves to the part of the exposition on related work.

## Composition of a motivation

A motivation serves three functions: it generates the question, shows that the question is non-trivial, and shows its significance. Each function is served by one of several strategies, and the strategies differ by the ideas that they present: ^motivation-composition

| Function | Strategy | Ideas presented |
| --- | --- | --- |
| Generate the question | **Tension**: two accepted results, or a result and an observation, cannot hold jointly under current understanding, and the question asks how to resolve the inconsistency [alvesson2011] | the two results in tension, each indispensable |
| Generate the question | **Implicit assumption**: a premise shared across a tradition but never stated is shown to be consequential and violated in a relevant regime | the assumption, with the cited works as evidence of its prevalence rather than as achievements |
| Generate the question *(inference)* | **Regression from a desideratum**: an objective accepted in the field requires several conditions, and existing results establish all of them but one | each result, discharging one condition; the open condition, as the question |
| Generate the question *(inference)* | **Genetic reconstruction**: the history of the problem, told through the results that changed the formulation of the question | the reductions, the impossibility results and the reformulations; a result that only improves a constant within a fixed formulation is left out |
| Show non-triviality | **Minimal witnessing instance**: a minimal case, such as a counterexample or a toy construction, in which established methods break | the instance; its minimality shows that the failure is structural |
| Show significance | **Decision relevance**: the difference that the answer makes, such as a choice of method or the validity of a common practice | the possible answers, and the change that each answer brings |

A minimal witnessing instance concerns the subject of the exposition. Therefore, in a source-bound exposition, the instance must reference a unit of a source, and an authored illustration cannot carry it. By contrast, when a statement of significance concerns the practice of the audience, that statement can be an authored motivation. The [admitted forms of a relation with an authored idea](../adr/provenance-of-ideas.md#^authored-relations) include the relation `motivation`.

A seventh strategy states the question in the first sentence, and then justifies the question as open, as non-trivial and as tractable now. *(Inference: the source assigns this strategy to no function of the table.)*

The strategies combine. A complete motivation takes one strategy that generates the question, tension or an implicit assumption, then the minimal witnessing instance, then decision relevance. The motivation is written backward from the question. Each sentence stays only when, without it, the question would become less determinate, less justified or less urgent. The [proposals on the order of ideas](../proposals/order-of-ideas.md#^question-first) place the question relative to the results that it makes relevant.

---
## Sources

> [!NOTE] Status of the claims
> - **Established:** the definition of each relation of Rhetorical Structure Theory by its effect on the reader; problematization as a source of research questions; as cited.
> - **Proposals:**
> 	- the reading of every test of selection as a test of presentation, and one test derived from the effect of each relation;
> 	- the rows of the retention test, restated from the [retention test of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/abstracts/argument.md#L46-L57);
> 	- the rows marked *(inference)*: each row has no counterpart in that source, or adds a criterion by a reading of this note;
> 	- the exclusions tied to an audience, restated from the [rule on excluded claims of an abstract](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/abstracts/argument.md#L44);
> 	- the roles of a prior result, the deletion test and the composition of a motivation, restated from the [motivation of a research work](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/writing/motivate-research.md);
> 	- the facts of a research source that admit a prior result, stated in the terms of `gnomon`.

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [alvesson2011] ○ [Alvesson & Sandberg, "Generating research questions through problematization", *Academy of Management Review* 36(2), 247–271, 2011](https://doi.org/10.5465/amr.2009.0188); problematization against gap-spotting
- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the effect of each relation
