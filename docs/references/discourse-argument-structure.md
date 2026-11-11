---
tags:
  - reference
index: "[References](docs/references/_index.md)"
aliases:
  - Accounts of discourse and argument structure
---
# Accounts of discourse and argument structure

## Objective

Four accounts describe how the parts of a text or of an argument relate: Rhetorical Structure Theory, the Argument Interchange Format, the model of Toulmin, and the theory of the question under discussion. The four accounts differ in the unit that they relate and in the kinds of relation that they separate. The [comparison](#^comparison) at the end of this note sets them side by side.

## Rhetorical Structure Theory

Rhetorical Structure Theory relates the spans of a text. Most relations are mononuclear: they join a nucleus, the span more central to the purpose of the writer, and a satellite that serves it. A few relations are multinuclear, such as a sequence or a contrast, and join spans of equal weight. Each relation is defined by constraints on the nucleus, on the satellite and on their combination, and by the effect that the writer intends on the reader. The relations fall into two kinds. A subject-matter relation, such as a cause or an elaboration, aims at the reader recognizing a relation between the contents of the spans. A presentational relation, such as a motivation or an evidence, aims at increasing an inclination of the reader, such as belief or the ability to understand. The analysis of a whole text forms a tree of spans, and that tree reduces to one central nucleus [mann1988]. ^rst

## Argument Interchange Format

The Argument Interchange Format represents an argument as a graph, so that tools of argumentation can exchange it. Its information nodes hold propositions, and its scheme nodes hold the application of a scheme to those propositions. Two information nodes connect only through a scheme node, so each relation between propositions states its kind. The specification of 2006 separates three kinds of scheme node [chesnevar2006]: ^aif

- a rule application records an inference;
- a conflict application records a conflict between propositions;
- a preference application records a preference between propositions.

> [!WARNING] Third kind of scheme not checked
> The [survey of link types of `geonexus`](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/practice/argument-specification/argument-spec-goal-oriented.md#L60-L85), from which this note is carried, listed rephrasing as the third kind of relation of the same article. Standard accounts of the format place preference application in the specification of 2006, and a scheme of rephrasing in later extensions. Neither reading was checked against the article.

## The model of Toulmin

The model of Toulmin assigns distinct roles to the statements of one argument. The data are the facts appealed to. The claim is the conclusion drawn from them. The warrant licenses the step from the data to the claim, and the backing supports the warrant. The qualifier states the strength with which the claim follows, such as "presumably". The rebuttal states the conditions under which the warrant does not apply. The model separates the data from the warrant: the data state the basis of the claim, whereas the warrant states why that basis leads to the claim [toulmin1958]. ^toulmin

## Questions under discussion

The theory of the question under discussion describes a discourse as organized by the questions that its participants pursue. The questions form a stack: a question accepted into the discourse stays under discussion until it is answered or abandoned. An assertion is relevant when it addresses, fully or partially, the question currently under discussion. A strategy of inquiry breaks a question into subquestions, each of whose answers contributes to the answer of the question above it [roberts2012]. ^qud

## Comparison

| Account | Unit related | Relations distinguished | Purpose |
| --- | --- | --- | --- |
| Rhetorical Structure Theory | the spans of a text | subject-matter against presentational relations; mononuclear against multinuclear relations | the analysis of the coherence of a text |
| Argument Interchange Format | the propositions of an argument | inference, conflict and preference | the exchange of arguments between tools |
| Model of Toulmin | the statements of one argument | the roles of data, claim, warrant, backing, qualifier and rebuttal | the analysis of an argument in practice |
| Question under discussion | the moves of a discourse | a question and its answers; a question and its subquestions | the relevance of an assertion |

^comparison

Annotators of a corpus analysed under Rhetorical Structure Theory agree more often on the structure of a text than on the labels of its relations [carlson2003]. ^label-agreement

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [carlson2003] ○ Carlson, Marcu & Okurowski, "Building a discourse-tagged corpus in the framework of Rhetorical Structure Theory", in van Kuppevelt & Smith (eds.), *Current and New Directions in Discourse and Dialogue*, Springer, 85–112, 2003; agreement of annotators on structure and on labels
- [chesnevar2006] ○ [Chesñevar, McGinnis, Modgil, Rahwan, Reed, Simari, South, Vreeswijk & Willmott, "Towards an argument interchange format", *The Knowledge Engineering Review* 21(4), 293–316, 2006](https://doi.org/10.1017/S0269888906001044); information nodes and scheme nodes
- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the relations, their nuclearity and their effects
- [roberts2012] ○ [Roberts, "Information structure in discourse: towards an integrated formal theory of pragmatics", *Semantics and Pragmatics* 5(6), 1–69, 2012](https://doi.org/10.3765/sp.5.6); the stack of questions under discussion
- [toulmin1958] ○ Toulmin, *The Uses of Argument*, Cambridge University Press, 1958; the layout of an argument
